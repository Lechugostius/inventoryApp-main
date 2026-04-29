from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.routes.auth import ensure_user_exists
from app.service.database.item_owner_service import get_all_item_owners
from app.service.database.items_service import get_item_by_id
from app.service.database.movement_service import add_movement
from app.service.database.movement_types_service import get_all_movement_types
from app.service.database.items_service import update_item
# NUEVOS IMPORTS para tiendas
from app.service.database.paises_service import get_all_paises
from app.service.database.tiendas_service import get_all_tiendas, get_tiendas_by_pais, get_tienda_by_id


registrarSalida_bp = Blueprint("registrarSalida", __name__)


@registrarSalida_bp.route("/registrarSalida", methods=["GET", "POST"])
def registrar_salida():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    try:
        if request.method == "GET":
            user_info = session["user"]
            # Datos existentes
            all_movement_types = get_all_movement_types()
            
            # FILTRAR SOLO TIPOS DE SALIDA (excluir "Entrada")
            # Basándome en tus datos: 1=Salida[Cambio], 2=Salida[AperturaRestaurante], 3=Otro, 4=Entrada
            movement_types = [
                mt for mt in all_movement_types 
                if mt.get('Name', '').lower() != 'entrada' and mt.get('ID') != 4
            ]
            
            departments = get_all_item_owners()
            # NUEVOS DATOS: Países y tiendas
            paises = get_all_paises()
            tiendas = get_all_tiendas()

            print(f"Tipos de movimiento filtrados: {[mt.get('Name') for mt in movement_types]}")  # Debug

            return render_template(
                "registrarSalida.html",
                user=user_info,
                movement_types=movement_types,
                departments=departments,
                paises=paises,
                tiendas=tiendas,
            )

        elif request.method == "POST":
            data = request.form.to_dict()
            print("Datos de salida recibidos:", data)  # Debug

            # Obtener el ID local del usuario
            user = session.get("user", {})
            user_id = user.get("local_id")

            if not user_id:
                user_id = ensure_user_exists(user)

            if not user_id:
                raise ValueError("No se pudo obtener el ID del usuario")

            # Procesar items seleccionados
            selected_items_json = data.get("selected_items")
            if not selected_items_json:
                raise ValueError("No se han seleccionado items")

            import json
            selected_items = json.loads(selected_items_json)
            
            if not selected_items or len(selected_items) == 0:
                raise ValueError("No se han seleccionado items")

            # Validar campos requeridos
            required_fields = ['movement_type', 'movement_date', 'responsible_name']
            for field in required_fields:
                if not data.get(field):
                    raise ValueError(f"El campo {field.replace('_', ' ')} es requerido")

            # NUEVA LÓGICA: Determinar destino según tipo
            destination_type = data.get("destination_type", "department")  # Default a department
            
            if destination_type == "tienda":
                tienda_id = data.get("tienda_id")
                if not tienda_id:
                    raise ValueError("La tienda es requerida")
                
                # Obtener información de la tienda
                tienda = get_tienda_by_id(tienda_id)
                if not tienda:
                    raise ValueError("Tienda no encontrada")
                
                destination = f"Tienda: {tienda['siglas']} - {tienda['nombre_tienda']} ({tienda['pais_nombre']})"
            else:
                # Usar departamento (comportamiento original)
                department = data.get("department")
                if not department:
                    raise ValueError("El departamento es requerido")
                destination = f"Departamento: {department}"

            # PROCESAMIENTO MEJORADO CON VALIDACIÓN EN TIEMPO REAL
            all_movements = []
            errors = []
            successful_items = []

            print(f"Procesando {len(selected_items)} grupos/items seleccionados")  # Debug

            for i, selected_item in enumerate(selected_items):
                if selected_item.get('isGroup'):
                    # Procesar grupo de items
                    group_name = selected_item.get('groupName', f'Grupo {i+1}')
                    print(f"Procesando grupo: {group_name} con {len(selected_item.get('selectedSerials', []))} series")  # Debug
                    
                    for j, serial_info in enumerate(selected_item.get('selectedSerials', [])):
                        item_id = serial_info['itemId']
                        serial_number = serial_info.get('serial', 'Sin serie')
                        
                        try:
                            # RE-VALIDAR ITEM EN TIEMPO REAL
                            item = get_item_by_id(item_id)
                            if not item:
                                errors.append(f"❌ Item ID {item_id} (Serie: {serial_number}) no encontrado")
                                continue
                            
                            current_stock = item.get("Stock", 0)
                            print(f"Item {item_id} (Serie: {serial_number}) - Stock actual: {current_stock}")  # Debug
                            
                            if current_stock < 1:
                                errors.append(f"❌ {item['Name']} (Serie: {serial_number}) sin stock disponible")
                                continue
                            
                            # Crear movimiento individual
                            movement_data = {
                                "item_id": item_id,
                                "movement_type_id": int(data['movement_type']),
                                "quantity": 1,
                                "origin_user_id": user_id,  
                                "responsible_user_id": user_id,  
                                "destination": destination,
                                "notes": (
                                    f"Grupo: {group_name} - "
                                    f"Serie: {serial_number} - "
                                    f"Responsable: {data['responsible_name']} - "
                                    f"Email: {data.get('responsible_email', 'N/A')} - "
                                    f"Tel: {data.get('responsible_phone', 'N/A')} - "
                                    f"Notas: {data.get('notes', 'N/A')}"
                                ),
                            }
                            
                            # SOLO CREAR MOVIMIENTO (no actualizar stock manualmente)
                            # El add_movement ya actualiza el stock automáticamente
                            movement_result = add_movement(**movement_data)
                            print(f"Resultado del movimiento para item {item_id}: {movement_result}")  # Debug
                            
                            if movement_result:
                                all_movements.append(movement_result)
                                successful_items.append(f"✅ {item['Name']} (Serie: {serial_number})")
                                print(f"Movimiento creado exitosamente para item {item_id}")  # Debug
                            else:
                                errors.append(f"❌ Error creando movimiento para {item['Name']} (Serie: {serial_number})")
                                
                        except Exception as e:
                            error_msg = f"❌ Error procesando {serial_number}: {str(e)}"
                            errors.append(error_msg)
                            print(f"Excepción procesando item {item_id}: {str(e)}")  # Debug
                            continue
                else:
                    # Procesar item individual (comportamiento original)
                    item_id = selected_item['ID']
                    quantity = selected_item['quantity']
                    
                    try:
                        # RE-VALIDAR ITEM EN TIEMPO REAL
                        item = get_item_by_id(item_id)
                        if not item:
                            errors.append(f"❌ Item ID {item_id} no encontrado")
                            continue
                        
                        current_stock = item.get("Stock", 0)
                        print(f"Item individual {item_id} - Stock actual: {current_stock}, Solicitado: {quantity}")  # Debug
                        
                        if current_stock < quantity:
                            errors.append(f"❌ {item['Name']}: Stock insuficiente (Disponible: {current_stock}, Solicitado: {quantity})")
                            continue
                        
                        # Crear movimiento
                        movement_data = {
                            "item_id": item_id,
                            "movement_type_id": int(data['movement_type']),
                            "quantity": quantity,
                            "origin_user_id": user_id,
                            "responsible_user_id": user_id,  
                            "destination": destination,
                            "notes": (
                                f"Responsable: {data['responsible_name']} - "
                                f"Email: {data.get('responsible_email', 'N/A')} - "
                                f"Tel: {data.get('responsible_phone', 'N/A')} - "
                                f"Notas: {data.get('notes', 'N/A')}"
                            ),
                        }
                        
                        # SOLO CREAR MOVIMIENTO (no actualizar stock manualmente)
                        # El add_movement ya actualiza el stock automáticamente
                        movement_result = add_movement(**movement_data)
                        
                        if movement_result:
                            all_movements.append(movement_result)
                            successful_items.append(f"✅ {item['Name']} (Cantidad: {quantity})")
                            
                    except Exception as e:
                        error_msg = f"❌ Error procesando item {item_id}: {str(e)}"
                        errors.append(error_msg)
                        print(f"Excepción procesando item individual {item_id}: {str(e)}")  # Debug
                        continue

            # RESPUESTA MEJORADA CON DETALLES
            print(f"Procesamiento completado: {len(all_movements)} éxitos, {len(errors)} errores")  # Debug

            if len(all_movements) == 0:
                # Todos los items fallaron
                error_summary = "No se pudo registrar ningún movimiento:\n• " + "\n• ".join(errors)
                raise ValueError(error_summary)
                
            elif len(errors) > 0:
                # Algunos items fallaron, algunos tuvieron éxito
                return jsonify({
                    "success": True,
                    "message": f"Salida parcialmente registrada.\n\n✅ EXITOSOS ({len(all_movements)}):\n• " + "\n• ".join(successful_items) + f"\n\n❌ FALLARON ({len(errors)}):\n• " + "\n• ".join(errors),
                    "movements_count": len(all_movements),
                    "errors": errors,
                    "successful_items": successful_items,
                    "partial": True
                })
            else:
                # Todo salió bien
                return jsonify({
                    "success": True,
                    "message": f"🎉 Salida registrada exitosamente!\n\n✅ ITEMS PROCESADOS ({len(all_movements)}):\n• " + "\n• ".join(successful_items),
                    "movements_count": len(all_movements),
                    "successful_items": successful_items
                })

    except Exception as e:
        error_message = str(e)
        print("Error en registrar salida:", error_message)
        return jsonify({"error": error_message}), 400


# NUEVA RUTA: API para obtener tiendas por país
@registrarSalida_bp.route("/api/tiendas/by-pais/<int:pais_id>")
def get_tiendas_by_pais_api(pais_id):
    """API endpoint para obtener tiendas filtradas por país"""
    try:
        tiendas = get_tiendas_by_pais(pais_id)
        return jsonify(tiendas)
    except Exception as e:
        return jsonify({"error": str(e)}), 400