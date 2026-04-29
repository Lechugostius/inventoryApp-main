
from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from app.service.database.category_service import add_category, delete_category, get_all_categories, update_category


categorias_bp = Blueprint("categorias", __name__)

@categorias_bp.route("/categorias", methods=['GET', 'POST'])
def categorias():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    try:
        user_info = session["user"]
        categories = get_all_categories()
        return render_template("categorias.html",
                            user=user_info,
                            categories=categories)
    except Exception as e:
        error_message = str(e)
        print("Error en categorías:", error_message)
        return render_template("error.html", error_message=error_message)
    
@categorias_bp.route("/api/categorias", methods=['POST', 'PUT', 'DELETE'])
def manage_categorias():
    try:
        if request.method == 'POST':
            data = request.get_json()
            result = add_category(name=data['name'])
            return jsonify(result)
            
        elif request.method == 'PUT':
            data = request.get_json()
            result = update_category(
                category_id=data['id'],
                name=data['name']
            )
            return jsonify(result)
            
        elif request.method == 'DELETE':
            data = request.get_json()
            result = delete_category(category_id=data['id'])
            return jsonify(result)
            
    except Exception as e:
        return jsonify({"error": str(e)}), 400