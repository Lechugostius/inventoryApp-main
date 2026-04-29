from datetime import datetime
from flask import Blueprint, redirect, render_template, session, url_for

from app.service.database.items_service import get_all_items, get_item_by_id, get_items_by_filters
from app.service.database.movement_service import get_all_movements

dashboard_bp = Blueprint("dashboard", __name__)

def group_movements_by_item_and_type(movements):
    """
    Agrupa movimientos por nombre de item y tipo de movimiento
    """
    from app.service.database.items_service import get_item_by_id
    
    grouped = {}
    
    for movement in movements:
        # Obtener el nombre del item primero
        try:
            item = get_item_by_id(movement['ItemID'])
            item_name = item['Name'] if item else f"Item-{movement['ItemID']}"
        except:
            item_name = f"Item-{movement['ItemID']}"
        
        # Crear clave simple: nombre + tipo de movimiento
        group_key = f"{item_name}_{movement['MovementTypeID']}"
        
        if group_key not in grouped:
            grouped[group_key] = {
                'id': movement['ID'],  # ID del primer movimiento
                'item_id': movement['ItemID'],
                'item_name': item_name,
                'movement_type_id': movement['MovementTypeID'],
                'movement_type': '',  # Se llenará después
                'date': movement['Date'],
                'destination': movement.get('Destination', 'N/A'),
                'total_quantity': 0,
                'movement_count': 0,
                'serial_numbers': [],
                'movement_ids': [movement['ID']],
                'first_id': movement['ID'],
                'last_id': movement['ID']
            }
        else:
            # Actualizar IDs para el rango
            group = grouped[group_key]
            group['movement_ids'].append(movement['ID'])
            group['first_id'] = min(group['first_id'], movement['ID'])
            group['last_id'] = max(group['last_id'], movement['ID'])
        
        # Sumar cantidad y agregar detalles
        group = grouped[group_key]
        group['total_quantity'] += movement['Quantity']
        group['movement_count'] += 1
        
        # Usar la fecha más reciente
        if movement['Date'] > group['date']:
            group['date'] = movement['Date']
        
        # Extraer número de serie de las notas si existe
        notes = movement.get('Notes', '')
        if 'Serie:' in notes:
            try:
                # Buscar patrón "Serie: XXXXX"
                import re
                serial_match = re.search(r'Serie:\s*([A-Za-z0-9]+)', notes)
                if serial_match:
                    serial = serial_match.group(1).strip()
                    if serial and serial not in group['serial_numbers']:
                        group['serial_numbers'].append(serial)
            except:
                pass
    
    print("DEBUG - Grupos creados:", len(grouped))  # Debug
    for key, group in grouped.items():
        print(f"  {key}: {group['movement_count']} movimientos, {group['total_quantity']} cantidad")
    
    return list(grouped.values())

@dashboard_bp.route("/dashboard")
def dashboard():
    """Dashboard principal con movimientos agrupados"""
    if "user" not in session:
        return redirect(url_for("auth.login"))
    try:
        user_info = session.get("user")
        if not user_info:
            return redirect(url_for("auth.login"))
        
        # 1. Obtener todos los items y calcular el stock total
        all_items = get_all_items()
        total_stock = sum(item.get('Stock', 0) for item in all_items)
        
        # 2. Obtener items con bajo stock (menos de 5 unidades)
        low_stock_items = [item for item in all_items if item.get('Stock', 0) < 5]
        
        # 3. Obtener movimientos de hoy
        today_movements = get_all_movements()
        today = datetime.now().date()
        
        # Definir tipos de movimiento
        MOVEMENT_TYPES = {
            1: "Salida [Cambio]",      # Check-Out
            2: "Salida [AperturaRestaurante]",  # Return
            3: "Otro",                 # Transfer
            4: "Entrada"               # Entry
        }
        
        # FILTRADO MEJORADO DE MOVIMIENTOS RECIENTES (últimos 2 días)
        if today_movements:
            from datetime import timedelta
            yesterday = today - timedelta(days=1)
            
            # Incluir hoy Y ayer para capturar movimientos recientes
            recent_movements_filtered = [m for m in today_movements 
                                       if m['Date'].date() >= yesterday]
            
            print(f"DEBUG - Total movimientos: {len(today_movements)}")  # Debug
            print(f"DEBUG - Movimientos últimos 2 días: {len(recent_movements_filtered)}")  # Debug
            print(f"DEBUG - Fecha de hoy: {today}")  # Debug
            print(f"DEBUG - Desde fecha: {yesterday}")  # Debug
            
            # Debug: mostrar algunos movimientos recientes con fechas
            for i, m in enumerate(recent_movements_filtered[:5]):
                print(f"  Movimiento {i+1}: ID={m['ID']}, Tipo={m['MovementTypeID']}, Fecha={m['Date'].date()}, Item={m['ItemID']}")
            
            # Contar entradas y salidas de los últimos 2 días
            entries_recent = len([m for m in recent_movements_filtered 
                                 if m['MovementTypeID'] == 4])  # Entradas
            
            # INCLUIR TODOS LOS TIPOS DE SALIDA (1, 2, 3)
            exits_recent = len([m for m in recent_movements_filtered 
                              if m['MovementTypeID'] in [1, 2, 3]])  # Salidas
            
            print(f"DEBUG - Entradas últimos 2 días: {entries_recent}, Salidas últimos 2 días: {exits_recent}")  # Debug
            
            # Para mostrar en el dashboard, usar los valores recientes
            entries_today = entries_recent
            exits_today = exits_recent
            
        else:
            recent_movements_filtered = []
            entries_today = 0
            exits_today = 0
            print("DEBUG - No hay movimientos disponibles")  # Debug
        
        # 4. Agrupar últimos movimientos (últimos 7 días)
        if today_movements:
            # Obtener movimientos de los últimos 7 días
            from datetime import timedelta
            week_ago = today - timedelta(days=7)
            
            recent_movements = [m for m in today_movements 
                              if m['Date'].date() >= week_ago]
            
            # Agrupar movimientos
            grouped_movements = group_movements_by_item_and_type(recent_movements)
            
            # Enriquecer con tipos de movimiento
            latest_movements = []
            for group in sorted(grouped_movements, 
                              key=lambda x: x['date'], 
                              reverse=True)[:8]:  # Últimos 8 grupos
                
                group['movement_type'] = MOVEMENT_TYPES.get(
                    group['movement_type_id'], "Desconocido"
                )
                latest_movements.append(group)
                
        else:
            latest_movements = []
        
        print("DEBUG - Últimos movimientos agrupados:", len(latest_movements))  # Debug
        
        # 5. Obtener items críticos (agrupados por nombre)
        critical_items = {}
        for item in low_stock_items:
            name = item.get('Name', 'Sin nombre')
            if name not in critical_items:
                critical_items[name] = {
                    'Name': name,
                    'TotalStock': 0,
                    'ItemCount': 0,
                    'MinStock': float('inf'),
                    'CategoryName': '',
                    'StatusName': ''
                }
            
            critical_items[name]['TotalStock'] += item.get('Stock', 0)
            critical_items[name]['ItemCount'] += 1
            critical_items[name]['MinStock'] = min(
                critical_items[name]['MinStock'], 
                item.get('Stock', 0)
            )
        
        # Filtrar items críticos agrupados DESPUÉS de agrupar
        critical_items_list = sorted(
            [item for item in critical_items.values() if item['TotalStock'] < 5],
            key=lambda x: x['TotalStock']
        )[:5]
        
        # Calcular low_stock basado en grupos filtrados
        low_stock = len([item for item in critical_items.values() if item['TotalStock'] < 5])
        
        # 6. Preparar stats
        stats = {
            "total_items": total_stock,
            "low_stock": low_stock,
            "entries_today": entries_today,
            "exits_today": exits_today
        }
        
        print("DEBUG - Stats calculados:", stats)  # Debug
        print("DEBUG - Items críticos agrupados:", len(critical_items_list))  # Debug
        
        return render_template("dashboard.html",
                             user=user_info,
                             stats=stats,
                             movements=latest_movements,
                             critical_items=critical_items_list)
                             
    except Exception as e:
        error_message = str(e)
        print("ERROR en dashboard:", error_message)
        return render_template("dashboard.html", 
                             user=user_info if 'user_info' in locals() else session.get("user"),
                             error_message=error_message,
                             stats={},
                             movements=[],
                             critical_items=[])