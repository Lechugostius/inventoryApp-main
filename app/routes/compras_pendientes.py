from flask import Blueprint, render_template, jsonify, session, redirect, url_for, request

from app.service.database.items_service import get_all_items

compras_pendientes_bp = Blueprint("compras_pendientes", __name__)

# Umbral de stock mínimo (igual que el usado en dashboard.py)
MINIMUM_STOCK_THRESHOLD = 5

# Almacén en memoria del estado de cada producto pendiente.
# Mapea item_id -> 'pending' | 'purchased'
# NOTA: Al ser en memoria, el estado se reinicia cuando se reinicia el servidor.
# Si se necesita persistencia, mover esto a una tabla en la base de datos.
_purchase_status = {}


@compras_pendientes_bp.route("/compras-pendientes")
def compras_pendientes():
    """Renderiza la página de compras pendientes."""
    if "user" not in session:
        return redirect(url_for("auth.login"))
    return render_template("compras_pendientes.html", user=session["user"])


@compras_pendientes_bp.route("/api/pending-purchases", methods=["GET"])
def api_pending_purchases():
    """Devuelve los productos con stock por debajo del mínimo, agrupados por nombre."""
    if "user" not in session:
        return jsonify({"error": "No autorizado"}), 401

    try:
        all_items = get_all_items()

        # Agrupar por nombre y sumar stock (mismo enfoque que dashboard.py)
        grouped = {}
        for item in all_items:
            name = item.get("Name", "Sin nombre")
            stock = item.get("Stock", 0) or 0

            if name not in grouped:
                grouped[name] = {
                    "id": item.get("ID"),  # ID del primer item del grupo
                    "name": name,
                    "stock": 0,
                }
            grouped[name]["stock"] += stock

        # Filtrar los que están por debajo del mínimo
        pending = []
        for group in grouped.values():
            if group["stock"] < MINIMUM_STOCK_THRESHOLD:
                deficit = MINIMUM_STOCK_THRESHOLD - group["stock"]
                product_id = group["id"]
                pending.append({
                    "id": product_id,
                    "name": group["name"],
                    "stock": group["stock"],
                    "minimumStock": MINIMUM_STOCK_THRESHOLD,
                    "deficit": deficit,
                    "status": _purchase_status.get(product_id, "pending"),
                })

        # Ordenar: primero los pendientes, luego los ya pedidos; dentro de cada
        # grupo, los de mayor déficit primero
        pending.sort(key=lambda p: (p["status"] == "purchased", -p["deficit"]))

        return jsonify(pending)

    except Exception as e:
        print("Error en api_pending_purchases:", str(e))
        return jsonify({"error": str(e)}), 500


@compras_pendientes_bp.route("/api/pending-purchases/mark", methods=["POST"])
def api_mark_pending_purchase():
    """Marca un producto como 'purchased' o lo regresa a 'pending'."""
    if "user" not in session:
        return jsonify({"success": False, "error": "No autorizado"}), 401

    try:
        data = request.get_json() or {}
        product_id = data.get("productId")
        new_status = data.get("status")

        if product_id is None:
            return jsonify({"success": False, "error": "productId es requerido"}), 400

        if new_status not in ("pending", "purchased"):
            return jsonify({"success": False, "error": "status inválido"}), 400

        _purchase_status[int(product_id)] = new_status

        return jsonify({
            "success": True,
            "productId": product_id,
            "status": new_status,
        })

    except Exception as e:
        print("Error en api_mark_pending_purchase:", str(e))
        return jsonify({"success": False, "error": str(e)}), 500