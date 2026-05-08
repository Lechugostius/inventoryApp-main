from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from ..service.database.items_service import get_all_items, get_items_by_filters, get_item_by_id, update_item
from ..service.database.category_service import get_all_categories
from ..service.database.statuses_service import get_all_statuses

inventory_bp = Blueprint('inventory', __name__)

def group_similar_items(items):
    """
    Agrupa items similares por nombre, categoría y estado
    """
    grouped = {}
    
    for item in items:
        # Crear clave única para agrupar
        group_key = f"{item.get('Name', '').strip()}_{item.get('CategoryID', '')}_{item.get('StatusID', '')}"
        
        if group_key not in grouped:
            # Crear nuevo grupo
            grouped[group_key] = {
                'group_name': item.get('Name', ''),
                'category_id': item.get('CategoryID'),
                'category_name': '',  # Se llenará después
                'status_id': item.get('StatusID'),
                'status_name': '',    # Se llenará después
                'location': item.get('Location', ''),
                'description': item.get('Description', ''),
                'total_stock': 0,
                'total_items': 0,
                'average_cost': 0,
                'currency': item.get('Currency', 'USD'),
                'serial_numbers': [],
                'items': [],
                'latest_date': item.get('RegistrationDate')
            }
        
        # Agregar item al grupo
        group = grouped[group_key]
        group['items'].append(item)
        group['total_stock'] += item.get('Stock', 0)
        group['total_items'] += 1
        
        # Agregar número de serie si existe
        
        if item.get('UniqueIdentifier'):
            group['serial_numbers'].append({
                'id': item.get('ID'),
                'serial': item.get('UniqueIdentifier'),
                'stock': item.get('Stock', 0),  # ← NUEVA LÍNEA
                'cost': item.get('UnitCost') or 0,
                'date': item.get('RegistrationDate')
            })
        
        # Actualizar fecha más reciente
        if item.get('RegistrationDate') and item.get('RegistrationDate') > group['latest_date']:
            group['latest_date'] = item.get('RegistrationDate')
    
    # Calcular costo promedio para cada grupo
    for group_key, group in grouped.items():
        total_cost = sum((item.get('UnitCost') or 0) * (item.get('Stock') or 0) for item in group['items'])
        total_stock = group['total_stock']
        group['average_cost'] = total_cost / total_stock if total_stock > 0 else 0
    
    return list(grouped.values())

@inventory_bp.route("/inventario")
def inventario():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    try:
        user_info = session["user"]
        
        # Obtener parámetros de filtro
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        status = request.args.get('status', '')
        view_mode = request.args.get('view', 'grouped')  # grouped o individual
        
        # Obtener items filtrados
        items = get_items_by_filters(
            name=search if search else None,
            category_id=int(category) if category else None,
            status_id=int(status) if status else None
        ) or []
        
        # Obtener datos para los filtros
        categories = get_all_categories() or []
        statuses = get_all_statuses() or []
        
        # Enriquecer con nombres de categorías y estados
        category_dict = {cat['ID']: cat['Name'] for cat in categories}
        status_dict = {stat['ID']: stat['Name'] for stat in statuses}
        
        if view_mode == 'grouped':
            # Vista agrupada
            grouped_items = group_similar_items(items)
            
            # Agregar nombres de categoría y estado
            for group in grouped_items:
                group['category_name'] = category_dict.get(group['category_id'], 'Sin categoría')
                group['status_name'] = status_dict.get(group['status_id'], 'Sin estado')
            
            # Paginación para grupos
            items_per_page = 10
            total_groups = len(grouped_items)
            total_pages = max(1, (total_groups + items_per_page - 1) // items_per_page)
            start_idx = (page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            paginated_groups = grouped_items[start_idx:end_idx]
            
            return render_template("inventario.html",
                                 user=user_info,
                                 groups=paginated_groups,
                                 categories=categories,
                                 statuses=statuses,
                                 current_page=page,
                                 total_pages=total_pages,
                                 prev_page=page-1 if page > 1 else None,
                                 next_page=page+1 if page < total_pages else None,
                                 view_mode=view_mode,
                                 search=search,
                                 selected_category=category,
                                 selected_status=status)
        
        else:
            # Vista individual (original)
            items_per_page = 10
            total_items = len(items)
            total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)
            start_idx = (page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            paginated_items = items[start_idx:end_idx]
            
            # Enriquecer items con nombres
            for item in paginated_items:
                item['CategoryName'] = category_dict.get(item.get('CategoryID'), 'Sin categoría')
                item['StatusName'] = status_dict.get(item.get('StatusID'), 'Sin estado')

            return render_template("inventario.html",
                                 user=user_info,
                                 items=paginated_items,
                                 categories=categories,
                                 statuses=statuses,
                                 current_page=page,
                                 total_pages=total_pages,
                                 prev_page=page-1 if page > 1 else None,
                                 next_page=page+1 if page < total_pages else None,
                                 view_mode=view_mode,
                                 search=search,
                                 selected_category=category,
                                 selected_status=status)
                             
    except Exception as e:
        error_message = str(e)
        print("Error en inventario:", error_message)
        return render_template("inventario.html", 
                             error_message=error_message,
                             user=user_info,
                             items=[],
                             categories=[],
                             statuses=[],
                             current_page=1,
                             total_pages=1,
                             prev_page=None,
                             next_page=None)
    
@inventory_bp.route("/api/items/search")
def search_items():
    try:
        query = request.args.get('q', '')
        # Buscar por nombre o identificador único
        items = get_items_by_filters(name=query)
        
        # FILTRAR SOLO ITEMS CON STOCK > 0 PARA SALIDAS
        if items:
            available_items = []
            for item in items:
                stock = item.get('Stock', 0)
                if stock > 0:
                    available_items.append(item)
                else:
                    print(f"Item {item.get('ID')} ({item.get('Name')}) filtrado: stock = {stock}")  # Debug
            
            print(f"Items encontrados: {len(items)}, Items con stock: {len(available_items)}")  # Debug
            return jsonify(available_items)
        
        return jsonify(items or [])
    except Exception as e:
        print(f"Error en búsqueda: {str(e)}")
        return jsonify({"error": str(e)}), 400

@inventory_bp.route("/api/group/<group_name>/details")
def get_group_details(group_name):
    """API para obtener detalles de un grupo específico"""
    try:
        # Obtener todos los items del grupo
        all_items = get_all_items() or []
        group_items = [item for item in all_items if item.get('Name', '').strip() == group_name.strip()]
        
        if not group_items:
            return jsonify({"error": "Grupo no encontrado"}), 404
        
        # Preparar detalles del grupo
        group_details = {
            'name': group_name,
            'total_items': len(group_items),
            'total_stock': sum(item.get('Stock', 0) for item in group_items),
            'items': []
        }
        
        for item in group_items:
            group_details['items'].append({
                'id': item.get('ID'),
                'serial': item.get('UniqueIdentifier'),
                'description': item.get('Description'),
                'location': item.get('Location'),
                'stock': item.get('Stock'),
                'cost': item.get('UnitCost', 0),
                'currency': item.get('Currency', 'USD'),
                'date': item.get('RegistrationDate').isoformat() if item.get('RegistrationDate') else None
            })
        
        return jsonify(group_details)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Las demás rutas permanecen igual
@inventory_bp.route("/item/<int:item_id>")
def view_item(item_id):
    if "user" not in session:
        return redirect(url_for("auth.login"))
    try:
        user_info = session["user"]
        item = get_item_by_id(item_id)
        if not item:
            raise ValueError("Item no encontrado")
            
        # Obtener datos adicionales
        categories = get_all_categories() or []
        statuses = get_all_statuses() or []
        
        # Obtener proveedores y propietarios
        from app.service.database.suppliers_service import get_all_suppliers
        from app.service.database.item_owner_service import get_all_item_owners
        
        suppliers = get_all_suppliers() or []
        owners = get_all_item_owners() or []
        
        # Enriquecer el item con nombres de relaciones
        enriched_item = dict(item)
        
        # Buscar nombre de categoría
        if item.get('CategoryID'):
            category = next((c for c in categories if c['ID'] == item['CategoryID']), None)
            enriched_item['CategoryName'] = category['Name'] if category else 'Categoría no encontrada'
        else:
            enriched_item['CategoryName'] = 'Sin categoría'
            
        # Buscar nombre de estado
        if item.get('StatusID'):
            status = next((s for s in statuses if s['ID'] == item['StatusID']), None)
            enriched_item['StatusName'] = status['Name'] if status else 'Estado no encontrado'
        else:
            enriched_item['StatusName'] = 'Sin estado'
            
        # Buscar nombre de proveedor
        if item.get('SupplierID'):
            # Los suppliers vienen como tuplas, no como diccionarios
            supplier = None
            for s in suppliers:
                if isinstance(s, (list, tuple)) and len(s) >= 2 and s[0] == item['SupplierID']:
                    supplier = {'ID': s[0], 'Name': s[1]}
                    break
                elif isinstance(s, dict) and s.get('ID') == item['SupplierID']:
                    supplier = s
                    break
            enriched_item['SupplierName'] = supplier['Name'] if supplier else 'Proveedor no encontrado'
        else:
            enriched_item['SupplierName'] = 'Sin proveedor'
            
        # Buscar nombre de propietario
        if item.get('OwnerID'):
            owner = next((o for o in owners if o.get('ID') == item['OwnerID']), None)
            enriched_item['OwnerName'] = owner['Name'] if owner else 'Propietario no encontrado'
        else:
            enriched_item['OwnerName'] = 'Sin propietario'
        
        print(f"DEBUG - Item enriquecido: CategoryName={enriched_item.get('CategoryName')}, StatusName={enriched_item.get('StatusName')}, SupplierName={enriched_item.get('SupplierName')}")
        
        # Obtener movimientos específicos de este item
        from app.service.database.movement_service import get_all_movements
        all_movements = get_all_movements() or []
        
        # Filtrar movimientos de este item específico
        item_movements = [m for m in all_movements if m.get('ItemID') == item_id]
        
        # Definir tipos de movimiento
        MOVEMENT_TYPES = {
            1: "Salida [Cambio]",
            2: "Salida [AperturaRestaurante]", 
            3: "Otro",
            4: "Entrada"
        }
        
        # Enriquecer movimientos con información adicional
        enriched_movements = []
        for movement in sorted(item_movements, key=lambda x: x.get('Date', ''), reverse=True):
            try:
                # Obtener información del usuario responsable si existe
                from app.service.database.user_service import get_user_by_id
                responsible_user = None
                if movement.get('ResponsibleUserID'):
                    try:
                        responsible_user = get_user_by_id(movement['ResponsibleUserID'])
                    except:
                        pass
                
                enriched_movement = {
                    'ID': movement.get('ID'),
                    'id': movement.get('ID'),
                    'Type': MOVEMENT_TYPES.get(movement.get('MovementTypeID'), 'Desconocido'),
                    'type': MOVEMENT_TYPES.get(movement.get('MovementTypeID'), 'Desconocido'),
                    'type_id': movement.get('MovementTypeID'),
                    'MovementTypeID': movement.get('MovementTypeID'),
                    'Quantity': movement.get('Quantity', 0),
                    'quantity': movement.get('Quantity', 0),
                    'Date': movement.get('Date'),
                    'date': movement.get('Date'),
                    'Destination': movement.get('Destination', 'N/A'),
                    'destination': movement.get('Destination', 'N/A'),
                    'Notes': movement.get('Notes', ''),
                    'notes': movement.get('Notes', ''),
                    'responsible_user': responsible_user['Name'] if responsible_user else 'Usuario desconocido',
                    'responsible_user_id': movement.get('ResponsibleUserID'),
                    'ResponsibleUserID': movement.get('ResponsibleUserID'),
                    'OriginUserID': movement.get('OriginUserID')
                }
                
                # Extraer información adicional de las notas
                notes = movement.get('Notes', '')
                if 'Factura:' in notes:
                    try:
                        invoice_part = notes.split('Factura:')[1].split(' - ')[0].strip()
                        enriched_movement['invoice'] = invoice_part
                    except:
                        pass
                
                if 'Serie:' in notes:
                    try:
                        serial_part = notes.split('Serie:')[1].split(' - ')[0].strip()
                        enriched_movement['serial'] = serial_part
                    except:
                        pass
                        
                if 'Costo:' in notes:
                    try:
                        cost_part = notes.split('Costo:')[1].split(' - ')[0].strip()
                        enriched_movement['cost'] = cost_part
                    except:
                        pass
                
                enriched_movements.append(enriched_movement)
                
            except Exception as e:
                print(f"Error procesando movimiento {movement.get('ID')}: {str(e)}")
                continue
        
        return render_template("view_item.html",
                             user=user_info,
                             item=enriched_item,  # Usamos el item enriquecido
                             categories=categories,
                             statuses=statuses,
                             movements=enriched_movements)
                             
    except Exception as e:
        error_message = str(e)
        print("Error en view_item:", error_message)
        # Redirigir al inventario con mensaje de error en lugar de template error
        return redirect(url_for('main.inventory.inventario') + f"?error=Item no encontrado: {error_message}")

@inventory_bp.route("/item/<int:item_id>/edit", methods=['GET', 'POST'])
def edit_item(item_id):
    if "user" not in session:
        return redirect(url_for("auth.login"))
    try:
        if request.method == 'GET':
            user_info = session["user"]
            item = get_item_by_id(item_id)
            if not item:
                raise ValueError("Item no encontrado")
                
            categories = get_all_categories()
            statuses = get_all_statuses()
            
            return render_template("edit_item.html",
                                user=user_info,
                                item=item,
                                categories=categories,
                                statuses=statuses)
                                
        elif request.method == 'POST':
            data = request.form.to_dict()
            
            update_data = {
                "item_id": item_id,
                "name": data.get('name'),
                "description": data.get('description'),
                "category_id": int(data.get('category_id')),
                "status_id": int(data.get('status_id')),
                "location": data.get('location'),
                "stock": int(data.get('stock', 0))
            }
            
            result = update_item(**update_data)
            
            return jsonify({
                "success": True,
                "message": "Item actualizado exitosamente"
            })
            
    except Exception as e:
        error_message = str(e)
        print("Error en edit_item:", error_message)
        if request.method == 'POST':
            return jsonify({"error": error_message}), 400
        return render_template("error.html", error_message=error_message)


        #GET para el Checklist

@inventory_bp.route("/api/pending-purchases", methods=["GET"])
def get_pending_purchases():
    try:
        from ..service.database.database import execute_query
        
        query = """
            SELECT 
                i.ID,
                i.Name,
                i.Stock,
                i.MinimumStock,
                (i.MinimumStock - i.Stock) AS Deficit,
                COALESCE(pp.Status, 'pending') AS Status
            FROM Items i
            LEFT JOIN PendingPurchases pp ON i.ID = pp.ProductID AND pp.Status != 'finished'
            WHERE i.Stock < i.MinimumStock
            ORDER BY i.Name
        """
        
        results = execute_query(query)
        
        pending_items = []
        for row in results:
            pending_items.append({
                "id": row[0],
                "name": row[1],
                "stock": row[2],
                "minimumStock": row[3],
                "deficit": row[4],
                "status": row[5]
            })
        
        return jsonify(pending_items)
    except Exception as e:
        print(f"Error en get_pending_purchases: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
    #POST para Checklist

@inventory_bp.route("/api/pending-purchases/mark", methods=["POST"])
def mark_pending_purchase():
    try:
        from ..service.database.database import execute_query, execute_non_query
        
        data = request.get_json()
        product_id = data.get("productId")
        new_status = data.get("status")  # 'purchased' o 'pending'
        
        if not product_id:
            return jsonify({"error": "productId es requerido"}), 400
        
        if new_status not in ["purchased", "pending"]:
            return jsonify({"error": "status debe ser 'purchased' o 'pending'"}), 400
        
        if new_status == "purchased":
            # Verificar si ya existe un registro pendiente o comprado
            check_query = """
                SELECT ID, Status FROM PendingPurchases
                WHERE ProductID = ? AND Status != 'finished'
            """
            existing = execute_query(check_query, (product_id,))
            
            if existing and len(existing) > 0:
                # Actualizar el registro existente
                update_query = """
                    UPDATE PendingPurchases
                    SET Status = 'purchased', PurchaseDate = GETDATE()
                    WHERE ProductID = ? AND Status != 'finished'
                """
                execute_non_query(update_query, (product_id,))
            else:
                # Crear nuevo registro
                # Primero obtener el déficit del producto
                deficit_query = """
                    SELECT (MinimumStock - Stock) AS Deficit
                    FROM Items
                    WHERE ID = ?
                """
                deficit_result = execute_query(deficit_query, (product_id,))
                suggested_qty = deficit_result[0][0] if deficit_result and len(deficit_result) > 0 else 1
                
                insert_query = """
                    INSERT INTO PendingPurchases (ProductID, SuggestedQuantity, Status, PurchaseDate)
                    VALUES (?, ?, 'purchased', GETDATE())
                """
                execute_non_query(insert_query, (product_id, suggested_qty))
        
        elif new_status == "pending":
            # Cambiar a estado pending (desmarcar)
            update_query = """
                UPDATE PendingPurchases
                SET Status = 'pending', PurchaseDate = NULL
                WHERE ProductID = ? AND Status != 'finished'
            """
            execute_non_query(update_query, (product_id,))
        
        return jsonify({"success": True, "message": "Estado actualizado correctamente"})
        
    except Exception as e:
        print(f"Error en mark_pending_purchase: {str(e)}")
        return jsonify({"error": str(e)}), 500