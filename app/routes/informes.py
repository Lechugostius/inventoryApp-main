

from flask import Blueprint, redirect, render_template, session, url_for

from app.service.database.category_service import get_all_categories
from app.service.database.items_service import get_all_items
from app.service.database.movement_service import get_all_movements


informes_bp = Blueprint("informes", __name__)


@informes_bp.route("/informes")
def informes():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    try:
        user_info = session["user"]
        
        # Obtener estadísticas generales
        all_items = get_all_items()
        all_movements = get_all_movements()
        categories = get_all_categories()
        
        # Calcular estadísticas
        total_stock = sum(item['Stock'] for item in all_items)
        
        # Calcular movimientos por tipo
        entradas = len([m for m in all_movements if m['MovementTypeID'] == 2])
        salidas = len([m for m in all_movements if m['MovementTypeID'] == 1])
        
        # Calcular items por categoría
        items_by_category = {}
        for item in all_items:
            cat_name = next((c['Name'] for c in categories if c['ID'] == item['CategoryID']), 'Sin Categoría')
            items_by_category[cat_name] = items_by_category.get(cat_name, 0) + 1
        
        return render_template("informes.html",
                             user=user_info,
                             total_stock=total_stock,
                             entradas=entradas,
                             salidas=salidas,
                             items_by_category=items_by_category,
                             items=all_items,
                             movements=all_movements)
                             
    except Exception as e:
        error_message = str(e)
        print("Error en informes:", error_message)
        return render_template("error.html", error_message=error_message)