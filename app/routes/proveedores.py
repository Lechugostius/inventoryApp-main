

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from app.service.database.suppliers_service import add_supplier, delete_supplier, get_all_suppliers, update_supplier


proveedores_bp = Blueprint("proveedores", __name__)


@proveedores_bp.route("/proveedores", methods=['GET', 'POST'])
def proveedores():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    try:
        user_info = session["user"]
        suppliers = get_all_suppliers()
        return render_template("proveedores.html",
                             user=user_info,
                             suppliers=suppliers)
    except Exception as e:
        error_message = str(e)
        print("Error en proveedores:", error_message)
        return render_template("error.html", error_message=error_message)

@proveedores_bp.route("/api/proveedores", methods=['POST', 'PUT', 'DELETE'])
def manage_proveedores():
    try:
        if request.method == 'POST':
            data = request.get_json()
            result = add_supplier(
                name=data['name'],
                contact=data.get('contact'),
                phone=data.get('phone'),
                email=data.get('email'),
                address=data.get('address'),
                notes=data.get('notes')
            )
            return jsonify(result)
            
        elif request.method == 'PUT':
            data = request.get_json()
            result = update_supplier(
                supplier_id=data['id'],
                name=data['name'],
                contact=data.get('contact'),
                phone=data.get('phone'),
                email=data.get('email'),
                address=data.get('address'),
                notes=data.get('notes')
            )
            return jsonify(result)
            
        elif request.method == 'DELETE':
            data = request.get_json()
            result = delete_supplier(supplier_id=data['id'])
            return jsonify(result)
            
    except Exception as e:
        return jsonify({"error": str(e)}), 400