from datetime import datetime
from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from app.service.database.category_service import get_all_categories
from app.service.database.items_service import get_all_items
from app.service.database.database import get_connection

informes_bp = Blueprint("informes", __name__)


@informes_bp.route("/informes")
def informes():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    try:
        user_info = session["user"]
        all_items = get_all_items()
        categories = get_all_categories()

        total_stock = sum(item['Stock'] for item in all_items)

        # Entradas = MovementTypeID 4, Salidas = 1,2,3
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Movements WHERE MovementTypeID = 4")
        entradas = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Movements WHERE MovementTypeID IN (1,2,3)")
        salidas = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        items_by_category = {}
        for item in all_items:
            cat_name = next((c['Name'] for c in categories if c['ID'] == item['CategoryID']), 'Sin Categoría')
            items_by_category[cat_name] = items_by_category.get(cat_name, 0) + 1

        return render_template("informes.html",
                               user=user_info,
                               total_stock=total_stock,
                               entradas=entradas,
                               salidas=salidas,
                               items_by_category=items_by_category)

    except Exception as e:
        print("Error en informes:", str(e))
        return render_template("error.html", error_message=str(e))


@informes_bp.route("/api/categorias-data")
def categorias_data():
    if "user" not in session:
        return jsonify({"error": "No autorizado"}), 401
    try:
        categories = get_all_categories()
        items = get_all_items()
        items_by_category = {}
        for item in items:
            cat_name = next((c['Name'] for c in categories if c['ID'] == item['CategoryID']), 'Sin Categoría')
            items_by_category[cat_name] = items_by_category.get(cat_name, 0) + 1
        return jsonify({
            "labels": list(items_by_category.keys()),
            "data": list(items_by_category.values())
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@informes_bp.route("/api/movimientos", methods=["GET"])
def api_movimientos():
    if "user" not in session:
        return jsonify({"error": "No autorizado"}), 401
    conn = get_connection()
    cursor = conn.cursor()
    try:
        granularidad = request.args.get("granularidad", "mes")
        fecha_str = request.args.get("fecha", "")

        if granularidad == "dia":
            if not fecha_str or len(fecha_str) != 7:
                return jsonify({"error": "Se requiere fecha en formato YYYY-MM"}), 400
            año, mes = map(int, fecha_str.split("-"))
            cursor.execute("""
                SELECT DAY(Date) as periodo,
                       SUM(CASE WHEN MovementTypeID = 4 THEN Quantity ELSE 0 END) as entradas,
                       SUM(CASE WHEN MovementTypeID IN (1,2,3) THEN Quantity ELSE 0 END) as salidas
                FROM Movements
                WHERE YEAR(Date) = ? AND MONTH(Date) = ?
                GROUP BY DAY(Date)
                ORDER BY periodo
            """, (año, mes))
            rows = cursor.fetchall()
            labels = [f"Día {r[0]}" for r in rows]
            entradas = [r[1] for r in rows]
            salidas = [r[2] for r in rows]

        elif granularidad == "semana":
            if not fecha_str or len(fecha_str) != 7:
                return jsonify({"error": "Se requiere fecha en formato YYYY-MM"}), 400
            año, mes = map(int, fecha_str.split("-"))
            # Traer movimientos del mes y agrupar por semana del mes
            cursor.execute("""
                SELECT
                    DATEPART(day, Date) as dia,
                    SUM(CASE WHEN MovementTypeID = 4 THEN Quantity ELSE 0 END) as entradas,
                    SUM(CASE WHEN MovementTypeID IN (1,2,3) THEN Quantity ELSE 0 END) as salidas
                FROM Movements
                WHERE YEAR(Date) = ? AND MONTH(Date) = ?
                GROUP BY DATEPART(day, Date)
                ORDER BY dia
            """, (año, mes))
            rows = cursor.fetchall()
            # Agrupar días en semanas
            from datetime import date
            import calendar
            _, days_in_month = calendar.monthrange(año, mes)
            weeks = []
            week_num = 1
            week_start = 1
            while week_start <= days_in_month:
                week_end = min(week_start + 6, days_in_month)
                week_entradas = sum(r[1] for r in rows if week_start <= r[0] <= week_end)
                week_salidas = sum(r[2] for r in rows if week_start <= r[0] <= week_end)
                meses_short = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
                label = f"{week_start} {meses_short[mes-1]} – {week_end} {meses_short[mes-1]}"
                weeks.append((label, week_entradas, week_salidas))
                week_start = week_end + 1
            labels = [w[0] for w in weeks]
            entradas = [w[1] for w in weeks]
            salidas = [w[2] for w in weeks]

        else:  # mes
            if fecha_str and len(fecha_str) == 7:
                año, mes = map(int, fecha_str.split("-"))
                cursor.execute("""
                    SELECT
                        SUM(CASE WHEN MovementTypeID = 4 THEN Quantity ELSE 0 END) as entradas,
                        SUM(CASE WHEN MovementTypeID IN (1,2,3) THEN Quantity ELSE 0 END) as salidas
                    FROM Movements
                    WHERE YEAR(Date) = ? AND MONTH(Date) = ?
                """, (año, mes))
                row = cursor.fetchone()
                nombre_mes = datetime(año, mes, 1).strftime("%b %Y")
                labels = [nombre_mes]
                entradas = [row[0] if row[0] else 0]
                salidas = [row[1] if row[1] else 0]
            else:
                cursor.execute("""
                    SELECT
                        YEAR(Date) as año,
                        MONTH(Date) as mes,
                        SUM(CASE WHEN MovementTypeID = 4 THEN Quantity ELSE 0 END) as entradas,
                        SUM(CASE WHEN MovementTypeID IN (1,2,3) THEN Quantity ELSE 0 END) as salidas
                    FROM Movements
                    GROUP BY YEAR(Date), MONTH(Date)
                    ORDER BY año DESC, mes DESC
                """)
                rows = cursor.fetchall()
                labels, entradas, salidas = [], [], []
                for r in rows:
                    labels.append(datetime(r[0], r[1], 1).strftime("%b %Y"))
                    entradas.append(r[2])
                    salidas.append(r[3])
                labels = labels[:12]
                entradas = entradas[:12]
                salidas = salidas[:12]

        return jsonify({"labels": labels, "entradas": entradas, "salidas": salidas})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()