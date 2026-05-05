from flask import Blueprint, render_template, jsonify, session, redirect, url_for, send_file
import io
from fpdf import FPDF
import pandas as pd
import xlsxwriter
from ..service.database.category_service import get_all_categories
from ..service.database.items_service import  get_all_items
from ..service.database.movement_service import get_all_movements

from datetime import datetime
from .dashboard import dashboard_bp
from .inventory import inventory_bp
from .nueva_entrada import nueva_entrada_bp
from .registrarSalida import registrarSalida_bp
from .categorias import categorias_bp
from .proveedores import proveedores_bp
from .informes import informes_bp
from .historial import historial_bp

main_bp = Blueprint("main", __name__)

main_bp.register_blueprint(dashboard_bp)
main_bp.register_blueprint(inventory_bp)
main_bp.register_blueprint(nueva_entrada_bp)
main_bp.register_blueprint(registrarSalida_bp)
main_bp.register_blueprint(categorias_bp)
main_bp.register_blueprint(proveedores_bp)
main_bp.register_blueprint(informes_bp)
main_bp.register_blueprint(historial_bp)

@main_bp.route("/")
def index():
    if "user" in session:
        return redirect(url_for("main.render_base"))
    return render_template("login.html")

@main_bp.route("/base")
def render_base():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    try:
        
        user_info = session["user"]
        print(user_info)
        # result = get_user_by_office_id(user_info["oid"])
        # print(get_users())
        # user_info = {
        #     "id": result[0][0],
        #     "name": result[0][1],
        #     "email": result[0][2],
        #     "role_name": result[0][3],
        #     "role_id": result[0][4],
        # }
        # print(f"userinfo: {user_info}")
        
        return render_template("index.html", user=user_info)
            
    except Exception as e:
        error_message = str(e)
        print("Error inesperado:", error_message)
        # if "Usuario con rol pendiente." in error_message:
        #     print("El usuario existe pero está pendiente de verificación.")
        # elif "Usuario no encontrado." in error_message:
        #     print("No se encontró ningún usuario con este office_id.")
        # else:
        #     print("Error inesperado:", error_message)
        #     return render_template("error.html", error_message=error_message)
        # return render_template("not_logged.html", user=user_info)

    
@main_bp.route("/api/export/pdf")
def export_pdf():
    try:
        # Obtener los datos necesarios
        all_items = get_all_items()
        all_movements = get_all_movements()
        categories = get_all_categories()
        
        from fpdf import FPDF
        
        pdf = FPDF()
        pdf.add_page()
        
        # Título
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(190, 10, 'Reporte de Inventario', 0, 1, 'C')
        
        # Fecha
        pdf.set_font('Arial', '', 10)
        pdf.cell(190, 10, f'Fecha: {datetime.now().strftime("%Y-%m-%d")}', 0, 1, 'R')
        
        # Estadísticas Generales
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(190, 10, 'Estadísticas Generales', 0, 1, 'L')
        
        pdf.set_font('Arial', '', 12)
        pdf.cell(60, 10, f'Stock Total: {sum(item["Stock"] for item in all_items)}', 0, 1)
        pdf.cell(60, 10, f'Total Items: {len(all_items)}', 0, 1)
        
        # Crear archivo temporal
        pdf_output = pdf.output(dest='S').encode('latin1')
        
        # Retornar el PDF
        return send_file(
            io.BytesIO(pdf_output),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='reporte_inventario.pdf'
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@main_bp.route("/api/export/excel")
def export_excel():
    try:
        import pandas as pd
        from io import BytesIO
        
        # Obtener los datos
        items = get_all_items()
        movements = get_all_movements()
        
        # Crear un Excel writer object
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Convertir datos a DataFrames
            df_items = pd.DataFrame(items)
            df_movements = pd.DataFrame(movements)
            
            # Escribir cada DataFrame en una hoja diferente
            df_items.to_excel(writer, sheet_name='Items', index=False)
            df_movements.to_excel(writer, sheet_name='Movimientos', index=False)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='inventario.xlsx'
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@main_bp.route("/compras-pendientes")
def compras_pendientes():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    
    user_info = session["user"]
    
    return render_template(
        "compras_pendientes.html",
        user=user_info
    )