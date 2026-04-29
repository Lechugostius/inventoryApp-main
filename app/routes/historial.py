from flask import Blueprint, jsonify, redirect, render_template, send_file, session, url_for

from app.service.database.change_history_service import get_all_change_history
from app.service.database.items_service import get_all_items
from app.service.database.movement_service import get_all_movements
from app.service.database.user_service import get_all_users


historial_bp = Blueprint("historial", __name__)


def filter_useful_changes(change_history):
    """Filtra cambios para mostrar solo información útil"""
    useful_changes = []
    
    for change in change_history:
        # FILTRAR: Eliminar cambios automáticos del trigger inútil
        if (change.get('ModifiedField') == 'General Update' and 
            change.get('PreviousValue') is None and 
            change.get('NewValue') is None):
            continue  # Saltar este cambio inútil
        
        # FILTRAR: Eliminar cambios donde anterior y nuevo son iguales
        if (change.get('PreviousValue') == change.get('NewValue') and 
            change.get('PreviousValue') is not None):
            continue  # Saltar cambios sin diferencia real
        
        # Mantener cambios con información real
        useful_changes.append(change)
    
    return useful_changes


def group_simultaneous_movements(movements):
    """Agrupa movimientos que ocurrieron en el mismo momento (mismo usuario, fecha y tipo)"""
    grouped = {}
    
    for move in movements:
        # Crear clave única: usuario + fecha (hasta minutos) + tipo + destino
        date_key = move['Date'].strftime('%Y-%m-%d %H:%M') if move.get('Date') else 'Sin fecha'
        key = f"{move.get('ResponsibleUserID', 'unknown')}_{date_key}_{move.get('MovementTypeID', 'unknown')}_{move.get('Destination', 'N/A')}"
        
        if key not in grouped:
            grouped[key] = {
                'movements': [],
                'first_movement': move,
                'total_items': 0
            }
        
        grouped[key]['movements'].append(move)
        grouped[key]['total_items'] += 1
    
    return grouped


@historial_bp.route("/historial")
def historial():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    try:
        user_info = session["user"]
        
        # Obtener datos básicos
        raw_change_history = get_all_change_history()
        raw_movements = get_all_movements()
        items = get_all_items()
        users = get_all_users()
        
        # APLICAR FILTROS
        useful_changes = filter_useful_changes(raw_change_history)
        grouped_movements = group_simultaneous_movements(raw_movements)
        
        print(f"Cambios originales: {len(raw_change_history)}, Útiles: {len(useful_changes)}")  # Debug
        print(f"Movimientos originales: {len(raw_movements)}, Grupos: {len(grouped_movements)}")  # Debug
        
        # Combinar la información filtrada
        history_data = []
        
        # Procesar cambios útiles
        for change in useful_changes:
            item = next((i for i in items if i['ID'] == change['ItemID']), None)
            user = next((u for u in users if u['ID'] == change['UserID']), None)
            
            history_data.append({
                'fecha': change['Date'],
                'tipo': 'Cambio',
                'item': item['Name'] if item else 'Desconocido',
                'usuario': user['Name'] if user else 'Desconocido',
                'detalles': f"Campo: {change['ModifiedField']}, Anterior: {change['PreviousValue']}, Nuevo: {change['NewValue']}",
                'grupo_size': 1,  # Los cambios no se agrupan
                'items_detalle': []
            })
        
        # Procesar movimientos agrupados
        for group_key, group_data in grouped_movements.items():
            first_move = group_data['first_movement']
            movements_list = group_data['movements']
            
            # Obtener usuario del primer movimiento
            user = next((u for u in users if u['ID'] == first_move['ResponsibleUserID']), None)
            
            # Determinar tipo de movimiento
            movement_type = 'Entrada' if first_move['MovementTypeID'] == 4 else 'Salida'
            if first_move['MovementTypeID'] == 1:
                movement_type = 'Salida'
            elif first_move['MovementTypeID'] == 2:
                movement_type = 'Salida [Apertura]'
            elif first_move['MovementTypeID'] == 3:
                movement_type = 'Otro'
            
            # Crear detalles de items
            items_detalle = []
            total_quantity = 0
            
            for move in movements_list:
                item = next((i for i in items if i['ID'] == move['ItemID']), None)
                if item:
                    items_detalle.append({
                        'name': item['Name'],
                        'quantity': move['Quantity'],
                        'serial': item.get('UniqueIdentifier', 'Sin serie')
                    })
                    total_quantity += move['Quantity']
            
            # Si hay múltiples items, crear entrada agrupada
            if len(movements_list) > 1:
                history_data.append({
                    'fecha': first_move['Date'],
                    'tipo': movement_type,
                    'item': f"Múltiples items ({len(movements_list)})",
                    'usuario': user['Name'] if user else 'Desconocido',
                    'detalles': f"Total: {total_quantity} unidades, Destino: {first_move['Destination'] or 'N/A'}",
                    'grupo_size': len(movements_list),
                    'items_detalle': items_detalle
                })
            else:
                # Item individual
                move = movements_list[0]
                item = next((i for i in items if i['ID'] == move['ItemID']), None)
                
                history_data.append({
                    'fecha': move['Date'],
                    'tipo': movement_type,
                    'item': item['Name'] if item else 'Desconocido',
                    'usuario': user['Name'] if user else 'Desconocido',
                    'detalles': f"Cantidad: {move['Quantity']}, Destino: {move['Destination'] or 'N/A'}",
                    'grupo_size': 1,
                    'items_detalle': []
                })
        
        # Ordenar por fecha descendente
        history_data.sort(key=lambda x: x['fecha'], reverse=True)
        
        print(f"Total entradas en historial final: {len(history_data)}")  # Debug
        
        return render_template("historial.html",
                             user=user_info,
                             history=history_data)
                             
    except Exception as e:
        error_message = str(e)
        print("Error en historial:", error_message)
        return render_template("error.html", error_message=error_message)


@historial_bp.route("/api/export/historial")
def export_historial():
    try:
        import pandas as pd
        from io import BytesIO
        
        # Obtener datos del historial (aplicando filtros también en la exportación)
        raw_change_history = get_all_change_history()
        raw_movements = get_all_movements()
        
        # Aplicar filtros para la exportación
        useful_changes = filter_useful_changes(raw_change_history)
        
        # Convertir a DataFrames (solo datos útiles)
        df_changes = pd.DataFrame(useful_changes)
        df_movements = pd.DataFrame(raw_movements)  # Movimientos completos para análisis
        
        # Crear Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_changes.to_excel(writer, sheet_name='Cambios_Utiles', index=False)
            df_movements.to_excel(writer, sheet_name='Movimientos', index=False)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='historial_filtrado.xlsx'
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400