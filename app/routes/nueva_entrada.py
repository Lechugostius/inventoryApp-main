import asyncio
from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from app.routes.auth import ensure_user_exists
from app.service.database.category_service import get_all_categories
from app.service.database.items_service import add_item, update_item
from app.service.database.movement_service import add_movement
from app.service.database.statuses_service import get_all_statuses
from app.service.database.suppliers_service import get_all_suppliers
from app.service.general_purpose import upload_blob
from app.service.database.files_service import add_file

nueva_entrada_bp = Blueprint("nueva_entrada", __name__)


def check_and_finish_pending_purchase(product_id):
    """Verifica si un producto ya no está bajo stock y actualiza su estado a finished"""
    try:
        from app.service.database.database import execute_query, execute_non_query
        
        query = """
            SELECT Stock, MinimumStock 
            FROM Items 
            WHERE ID = ?
        """
        result = execute_query(query, (product_id,))
        
        if not result:
            return
        
        stock = result[0][0]
        minimum_stock = result[0][1]
        
        if stock >= minimum_stock:
            update_query = """
                UPDATE PendingPurchases
                SET Status = 'finished'
                WHERE ProductID = ? AND Status IN ('pending', 'purchased')
            """
            execute_non_query(update_query, (product_id,))
            print(f"Producto {product_id} marcado como finished - Stock {stock} >= {minimum_stock}")
            
    except Exception as e:
        print(f"Error en check_and_finish_pending_purchase: {str(e)}")


@nueva_entrada_bp.route("/nueva-entrada", methods=["GET", "POST"])
def nueva_entrada():
    if "user" not in session:
        return redirect(url_for("auth.login"))

    try:
        if request.method == "GET":
            categories = get_all_categories()
            suppliers = get_all_suppliers()
            statuses = get_all_statuses()

            return render_template(
                "nueva-entrada.html",
                categories=categories,
                suppliers=suppliers,
                statuses=statuses,
            )

        elif request.method == "POST":
            data = request.form.to_dict()
            filesData = request.files.getlist("files")
            print("Datos del formulario recibidos:", data)
            
            unit_cost = data.get("unit_cost")
            if not unit_cost:
                return jsonify({"error": "El costo unitario es requerido"}), 400
            
            try:
                unit_cost = float(unit_cost)
                if unit_cost < 0:
                    return jsonify({"error": "El costo unitario no puede ser negativo"}), 400
            except ValueError:
                return jsonify({"error": "El costo unitario debe ser un número válido"}), 400

            currency = data.get("currency", "USD")
            if currency not in ['USD', 'CRC']:
                return jsonify({"error": "Moneda no válida"}), 400

            file_urls = []

            async def upload_files():
                for file in filesData:
                    if file.filename:
                        file_content = file.read()
                        file_url = await upload_blob(file.filename, file_content)
                        if file_url:
                            file_urls.append(file_url)

            asyncio.run(upload_files())

            user = session.get("user", {})
            user_id = user.get("local_id")

            if not user_id:
                user_id = ensure_user_exists(user)

            if not user_id:
                raise ValueError("No se pudo obtener el ID del usuario")

            try:
                item_data = {
                    "name": data.get("device_name"),
                    "description": data.get("model", ""),
                    "category_id": int(data.get("category_id")),
                    "unique_identifier": data.get("device_id"),
                    "supplier_id": int(data.get("supplier_id")),
                    "status_id": int(data.get("status_id")),
                    "location": data.get("location"),
                    "stock": int(data.get("quantity", 1)),
                    "unit_cost": unit_cost,
                    "currency": currency,
                }

                item_result = add_item(**item_data)
                item_id = item_result["ID"]

                # Verificar si debe quitarse del checklist de compras pendientes
                check_and_finish_pending_purchase(item_id)

                for file_url in file_urls:
                    add_file(item_id, file_url, "image")

                movement_data = {
                    "item_id": item_id,
                    "movement_type_id": 4,
                    "quantity": int(data.get("quantity", 1)),
                    "origin_user_id": user_id,
                    "responsible_user_id": user_id,
                    "destination": data.get("location"),
                    "notes": f"Factura: {data.get('invoice_number', 'N/A')} - Costo: {currency} {unit_cost} - Notas: {data.get('notes', '')}",
                }

                movement_result = add_movement(**movement_data)

                return jsonify({
                    "message": "Entrada registrada exitosamente",
                    "item_id": item_id,
                    "unit_cost": unit_cost,
                    "currency": currency,
                    "total_cost": unit_cost * int(data.get("quantity", 1))
                })

            except Exception as e:
                print(f"Error procesando la solicitud: {str(e)}")
                raise

    except Exception as e:
        error_message = str(e)
        print("Error en nueva entrada:", error_message)
        if request.method == "POST":
            return jsonify({"error": error_message}), 400
        return render_template("error.html", error_message=error_message)


@nueva_entrada_bp.route("/nueva-entrada-multiple", methods=["POST"])
def nueva_entrada_multiple():
    if "user" not in session:
        return jsonify({"error": "No autorizado"}), 401

    try:
        data = request.get_json()
        
        if not data.get("supplierId") or not data.get("entries"):
            return jsonify({"error": "Datos incompletos"}), 400
        
        invoice_currency = data.get("invoiceCurrency", "USD")
        if invoice_currency not in ['USD', 'CRC']:
            return jsonify({"error": "Moneda de factura no válida"}), 400
        
        user = session.get("user", {})
        user_id = user.get("local_id")
        
        if not user_id:
            user_id = ensure_user_exists(user)
            
        if not user_id:
            raise ValueError("No se pudo obtener el ID del usuario")

        successful_entries = []
        failed_entries = []
        total_cost_processed = 0
        
        for entry in data["entries"]:
            try:
                unit_cost = entry.get("unitCost")
                if not unit_cost:
                    failed_entries.append({
                        "serial": entry.get("serial", "Desconocido"),
                        "error": "Costo unitario requerido"
                    })
                    continue
                
                try:
                    unit_cost = float(unit_cost)
                    if unit_cost < 0:
                        failed_entries.append({
                            "serial": entry.get("serial", "Desconocido"),
                            "error": "Costo unitario no puede ser negativo"
                        })
                        continue
                except ValueError:
                    failed_entries.append({
                        "serial": entry.get("serial", "Desconocido"),
                        "error": "Costo unitario debe ser un número válido"
                    })
                    continue
                
                item_data = {
                    "name": entry["itemName"],
                    "description": f"{entry.get('description', '')} - Serie: {entry['serial']}",
                    "category_id": int(entry["categoryId"]),
                    "unique_identifier": entry["serial"],
                    "supplier_id": int(entry["supplierId"]),
                    "status_id": int(entry["statusId"]),
                    "location": entry["location"],
                    "stock": 1,
                    "unit_cost": unit_cost,
                    "currency": invoice_currency,
                }

                item_result = add_item(**item_data)
                
                if not item_result:
                    failed_entries.append({
                        "serial": entry["serial"],
                        "error": "Error al crear el item"
                    })
                    continue
                
                item_id = item_result["ID"]

                # Verificar si debe quitarse del checklist de compras pendientes
                check_and_finish_pending_purchase(item_id)

                movement_data = {
                    "item_id": item_id,
                    "movement_type_id": 4,
                    "quantity": 1,
                    "origin_user_id": user_id,
                    "responsible_user_id": user_id,
                    "destination": entry["location"],
                    "notes": f"Factura: {data.get('invoiceNumber', 'N/A')} - Fecha: {data.get('invoiceDate', 'N/A')} - Serie: {entry['serial']} - Costo: {invoice_currency} {unit_cost}",
                }

                movement_result = add_movement(**movement_data)
                
                if movement_result:
                    successful_entries.append({
                        "item_id": item_id,
                        "serial": entry["serial"],
                        "name": entry["itemName"],
                        "cost": unit_cost
                    })
                    total_cost_processed += unit_cost
                else:
                    failed_entries.append({
                        "serial": entry["serial"],
                        "error": "Error al registrar el movimiento"
                    })

            except Exception as e:
                failed_entries.append({
                    "serial": entry.get("serial", "Desconocido"),
                    "error": str(e)
                })

        response = {
            "message": f"Procesadas {len(successful_entries)} entradas exitosamente",
            "successful_count": len(successful_entries),
            "failed_count": len(failed_entries),
            "successful_entries": successful_entries,
            "failed_entries": failed_entries,
            "invoice_number": data.get("invoiceNumber", "N/A"),
            "currency": invoice_currency,
            "total_cost": total_cost_processed
        }

        if len(failed_entries) > 0:
            response["warning"] = f"Se produjeron {len(failed_entries)} errores durante el procesamiento"

        return jsonify(response)

    except Exception as e:
        error_message = str(e)
        print("Error en nueva entrada múltiple:", error_message)
        return jsonify({"error": error_message}), 400