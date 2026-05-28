from datetime import datetime, timedelta
from io import BytesIO

from flask import Blueprint, jsonify, request, send_file, session
from fpdf import FPDF

from app.service.database.database import execute_query

reports_bp = Blueprint("reports", __name__)

# === Paleta Taco Bell ===
COLOR_PURPLE_DARK = (92, 26, 141)       # #5C1A8D - header, títulos
COLOR_PURPLE_LIGHT = (247, 241, 251)    # #F7F1FB - filas alternas, cards suaves
COLOR_ORANGE = (255, 165, 0)            # #FFA500 - acentos, barras laterales
COLOR_ORANGE_BG = (255, 244, 224)       # #FFF4E0 - card crítica
COLOR_ORANGE_DARK = (168, 88, 0)        # #A85800 - texto sobre naranja
COLOR_RED = (220, 53, 69)               # #dc3545 - números críticos
COLOR_GREEN_DARK = (31, 122, 31)        # #1F7A1F - entradas
COLOR_TEXT = (44, 44, 42)               # #2C2C2A - texto principal
COLOR_TEXT_MUTED = (136, 136, 136)      # #888 - texto secundario
COLOR_WHITE = (255, 255, 255)
COLOR_BORDER = (230, 230, 230)
COLOR_RED_BG = (255, 224, 224)          # #FFE0E0 - fondo del badge de déficit
COLOR_RED_DARK = (176, 32, 32)          # #B02020 - texto del badge de déficit
COLOR_FOOTER_BG = (250, 250, 250)       # #FAFAFA - fondo del footer

class QuincenalPDF(FPDF):
    """PDF con header de marca Taco Bell, narrativa, cards y footer."""

    def __init__(self, fecha_desde, fecha_hasta, narrativa, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta
        self.narrativa = narrativa
        self.set_auto_page_break(auto=True, margin=22)

    def header(self):
        # Fondo morado del header (más alto que antes)
        self.set_fill_color(*COLOR_PURPLE_DARK)
        self.rect(0, 0, 210, 28, "F")

        # Bloque "TB" naranja (placeholder de logo) a la izquierda
        self.set_fill_color(*COLOR_ORANGE)
        self.rect(12, 7, 14, 14, "F")
        self.set_xy(12, 7)
        self.set_text_color(*COLOR_PURPLE_DARK)
        self.set_font("Helvetica", "B", 13)
        self.cell(14, 14, "TB", 0, 0, "C")

        # Título y rango de fechas
        self.set_xy(30, 9)
        self.set_text_color(*COLOR_WHITE)
        self.set_font("Helvetica", "B", 13)
        self.cell(120, 5, "Reporte Quincenal", 0, 2)
        self.set_x(30)
        self.set_font("Helvetica", "", 8)
        meses = ["ene", "feb", "mar", "abr", "may", "jun",
                 "jul", "ago", "sep", "oct", "nov", "dic"]
        m_desde = meses[self.fecha_desde.month - 1]
        m_hasta = meses[self.fecha_hasta.month - 1]
        if self.fecha_desde.month == self.fecha_hasta.month:
            rango = f"{self.fecha_desde.day} - {self.fecha_hasta.day} de {m_hasta} {self.fecha_hasta.year}"
        else:
            rango = f"{self.fecha_desde.day} {m_desde} - {self.fecha_hasta.day} {m_hasta} {self.fecha_hasta.year}"
        self.set_text_color(220, 200, 240)  # morado muy claro
        self.cell(120, 4, rango, 0, 0)

        # Marca a la derecha
        self.set_xy(150, 11)
        self.set_text_color(*COLOR_ORANGE)
        self.set_font("Helvetica", "B", 8)
        self.cell(50, 4, "TACO BELL", 0, 2, "R")
        self.set_x(150)
        self.set_text_color(180, 150, 220)
        self.set_font("Helvetica", "", 6)
        self.cell(50, 3, "Inventario", 0, 0, "R")

        # Acento naranja en la base del header
        self.set_fill_color(*COLOR_ORANGE)
        self.rect(0, 28, 73, 2, "F")

        # Espacio bajo el header
        self.set_y(36)
        self.set_text_color(*COLOR_TEXT)

    def footer(self):
        # Fondo del footer
        self.set_fill_color(*COLOR_FOOTER_BG)
        self.rect(0, 285, 210, 12, "F")

        self.set_y(-10)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*COLOR_TEXT_MUTED)
        fecha_gen = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.set_x(12)
        self.cell(95, 4, f"{fecha_gen} - Generado automaticamente", 0, 0, "L")

        # Marca + paginación a la derecha
        self.set_x(107)
        self.set_text_color(*COLOR_PURPLE_DARK)
        self.set_font("Helvetica", "B", 7)
        self.cell(40, 4, "TACO BELL", 0, 0, "R")
        self.set_text_color(*COLOR_TEXT_MUTED)
        self.set_font("Helvetica", "", 7)
        self.cell(5, 4, "  |  ", 0, 0, "C")
        self.cell(46, 4, f"Pagina {self.page_no()} de {{nb}}", 0, 0, "L")

    def draw_narrativa(self):
        """Bloque de resumen en lenguaje natural debajo del header."""
        y = self.get_y()
        # Fondo morado pálido + barra naranja
        self.set_fill_color(*COLOR_PURPLE_LIGHT)
        self.rect(12, y, 186, 16, "F")
        self.set_fill_color(*COLOR_ORANGE)
        self.rect(12, y, 1.5, 16, "F")

        # Label
        self.set_xy(16, y + 2.5)
        self.set_text_color(*COLOR_PURPLE_DARK)
        self.set_font("Helvetica", "B", 7)
        self.cell(180, 3, "RESUMEN DEL PERIODO", 0, 0)

        # Texto
        self.set_xy(16, y + 7)
        self.set_text_color(*COLOR_TEXT)
        self.set_font("Helvetica", "", 9)
        self.multi_cell(178, 4.2, self.narrativa)

        self.set_y(y + 20)

    def section_title(self, titulo, subtitulo=None):
        """Título de sección: barra naranja + texto morado + (opcional) conteo gris."""
        self.ln(3)
        y = self.get_y()
        self.set_fill_color(*COLOR_ORANGE)
        self.rect(12, y + 0.5, 1.5, 5, "F")
        self.set_xy(16, y)
        self.set_text_color(*COLOR_PURPLE_DARK)
        self.set_font("Helvetica", "B", 11)
        self.cell(140, 6, titulo, 0, 0)
        if subtitulo:
            self.set_text_color(*COLOR_TEXT_MUTED)
            self.set_font("Helvetica", "", 8)
            self.cell(40, 6, subtitulo, 0, 0, "R")
        self.ln(8)

    def stat_card(self, x, y, w, h, label, value, sub, variant="purple"):
        """Tarjeta de stat con números grandes y borde superior naranja."""
        if variant == "critical":
            fill = COLOR_ORANGE_BG
            text_color = COLOR_ORANGE_DARK
            value_color = COLOR_ORANGE_DARK
            top_border = True
        elif variant == "purple":
            fill = COLOR_PURPLE_DARK
            text_color = (220, 200, 240)
            value_color = (255, 255, 255)
            top_border = True
        else:
            fill = COLOR_PURPLE_LIGHT
            text_color = COLOR_PURPLE_DARK
            value_color = COLOR_PURPLE_DARK
            top_border = False

        # Fondo
        self.set_fill_color(*fill)
        self.rect(x, y, w, h, "F")

        # Borde superior naranja para las cards "fuertes"
        if top_border:
            self.set_fill_color(*COLOR_ORANGE)
            self.rect(x, y, w, 1.2, "F")

        # Label en mayúsculas
        self.set_xy(x + 3, y + 4)
        self.set_text_color(*text_color)
        self.set_font("Helvetica", "B", 6)
        self.cell(w - 6, 3, label.upper(), 0, 2)

        # Valor grande
        self.set_xy(x + 3, y + 9)
        self.set_text_color(*value_color)
        self.set_font("Helvetica", "B", 22)
        self.cell(w - 6, 10, str(value), 0, 2)

        # Subtítulo
        self.set_xy(x + 3, y + 21)
        self.set_text_color(*text_color)
        self.set_font("Helvetica", "", 6)
        self.cell(w - 6, 3, sub, 0, 0)

def _safe(value, default=""):
    """Convierte None a default, asegura string para FPDF."""
    if value is None:
        return default
    return str(value)


def _truncate(text, max_len):
    """Trunca texto con '...' si excede max_len caracteres."""
    text = _safe(text)
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def _build_pdf(fecha_desde, fecha_hasta):
    """Genera el PDF en memoria y lo devuelve como bytes."""

    # === 1. Consultas a la BD ===

    total_items_result = execute_query(
        "SELECT COUNT(DISTINCT Name) AS Total FROM Items WHERE StatusID != 4"
    )
    total_items = total_items_result[0]["Total"] if total_items_result else 0

    stock_bajo = execute_query(
        """
        SELECT
            MIN(i.ID)           AS ID,
            i.Name              AS Name,
            SUM(i.Stock)        AS TotalStock,
            MAX(i.MinimumStock) AS MinimumStock,
            (MAX(i.MinimumStock) - SUM(i.Stock)) AS Deficit
        FROM Items i
        WHERE i.StatusID != 4
        GROUP BY i.Name
        HAVING SUM(i.Stock) < MAX(i.MinimumStock)
        ORDER BY (MAX(i.MinimumStock) - SUM(i.Stock)) DESC
        """
    )

    pendientes_sin_marcar = execute_query(
        """
        SELECT
            i.Name                                  AS Name,
            SUM(i.Stock)                            AS TotalStock,
            MAX(i.MinimumStock)                     AS MinimumStock,
            (MAX(i.MinimumStock) - SUM(i.Stock))    AS Deficit
        FROM Items i
        LEFT JOIN PendingPurchases pp
        ON i.ID = pp.ProductID AND pp.Status = 'purchased'
        WHERE i.StatusID != 4
        AND pp.ID IS NULL
        GROUP BY i.Name
        HAVING SUM(i.Stock) < MAX(i.MinimumStock)
        ORDER BY (MAX(i.MinimumStock) - SUM(i.Stock)) DESC
        """
    )

    movimientos = execute_query(
        """
        SELECT TOP 60
            m.ID,
            m.Date,
            m.MovementTypeID,
            m.Quantity,
            m.Destination,
            i.Name AS ItemName
        FROM Movements m
        LEFT JOIN Items i ON m.ItemID = i.ID
        WHERE m.Date >= ? AND m.Date <= ?
        ORDER BY m.Date DESC
        """,
        (fecha_desde, fecha_hasta),
    )

    movimientos_count_result = execute_query(
        "SELECT COUNT(*) AS Total FROM Movements WHERE Date >= ? AND Date <= ?",
        (fecha_desde, fecha_hasta),
    )
    movimientos_count = movimientos_count_result[0]["Total"] if movimientos_count_result else 0

    # === 2. Construir narrativa en lenguaje natural ===

    n_critico = len(stock_bajo)
    n_pend = len(pendientes_sin_marcar)
    if n_critico == 0 and movimientos_count == 0:
        narrativa = (
            "Periodo sin movimientos registrados y sin items en stock critico. "
            "Inventario en estado estable."
        )
    elif n_critico == 0:
        narrativa = (
            f"Esta quincena registra {movimientos_count} movimientos. "
            "Todos los productos mantienen stock por encima del minimo. Sin acciones urgentes."
        )
    else:
        partes = [f"Esta quincena registra {movimientos_count} movimientos"]
        partes.append(f"{n_critico} items con stock por debajo del minimo")
        if n_pend > 0:
            partes.append(f"de los cuales {n_pend} aun no han sido marcados como pedidos")
        narrativa = ". ".join(partes[:2])
        if n_pend > 0:
            narrativa += f", {partes[2]}."
        else:
            narrativa += "."

    # === 3. Generar PDF ===

    pdf = QuincenalPDF(fecha_desde, fecha_hasta, narrativa)
    pdf.alias_nb_pages()
    pdf.add_page()

    # --- Narrativa ---
    pdf.draw_narrativa()

    # --- Stats cards ---
    pdf.section_title("Resumen ejecutivo")

    y_cards = pdf.get_y()
    card_w = 45
    card_h = 26
    gap = 2
    x_start = 12

    pdf.stat_card(x_start, y_cards, card_w, card_h,
                  "Inventario", total_items, "productos activos", "purple")
    pdf.stat_card(x_start + (card_w + gap), y_cards, card_w, card_h,
                  "Stock critico", len(stock_bajo), "requieren accion", "critical")
    pdf.stat_card(x_start + 2 * (card_w + gap), y_cards, card_w, card_h,
                  "Movimientos", movimientos_count, "en 15 dias", "neutral")
    pdf.stat_card(x_start + 3 * (card_w + gap), y_cards, card_w, card_h,
                  "Pendientes", len(pendientes_sin_marcar), "sin pedir aun", "neutral")

    pdf.set_y(y_cards + card_h + 4)

    # --- Items con stock bajo ---
    pdf.section_title("Items con stock bajo", f"{len(stock_bajo)} productos")

    if stock_bajo:
        deficit_total = sum(row["Deficit"] for row in stock_bajo)
        _draw_table(
            pdf,
            headers=[("Producto", 95), ("Actual", 25), ("Minimo", 25), ("Deficit", 41)],
            rows=[
                [
                    _truncate(row["Name"], 47),
                    str(row["TotalStock"]),
                    str(row["MinimumStock"]),
                    f"-{row['Deficit']}",
                ]
                for row in stock_bajo
            ],
            critical_col_index=1,
            badge_col_index=3,
            total_row=("Total deficit acumulado", f"{deficit_total} unidades"),
        )
    else:
        _draw_empty(pdf, "No hay items con stock bajo. Todo en orden.")

    # --- Compras pendientes sin marcar ---
    if pdf.get_y() > 220:
        pdf.add_page()

    pdf.section_title("Compras pendientes sin marcar", f"{len(pendientes_sin_marcar)} productos")

    if pendientes_sin_marcar:
        a_pedir_total = sum(row["Deficit"] for row in pendientes_sin_marcar)
        _draw_table(
            pdf,
            headers=[("Producto", 110), ("Stock", 30), ("A pedir", 46)],
            rows=[
                [
                    _truncate(row["Name"], 55),
                    str(row["TotalStock"]),
                    str(row["Deficit"]),
                ]
                for row in pendientes_sin_marcar
            ],
            critical_col_index=2,
            total_row=("Total a pedir", f"{a_pedir_total} unidades"),
        )
    else:
        _draw_empty(pdf, "No hay compras pendientes sin atender.")

    # --- Movimientos del período ---
    pdf.add_page()
    pdf.section_title("Movimientos del periodo", f"{movimientos_count} registros")

    if movimientos:
        movement_type_names = {1: "Salida (Cambio)", 2: "Salida (Apertura)", 3: "Otro", 4: "Entrada"}
        _draw_table(
            pdf,
            headers=[
                ("Fecha", 22),
                ("Item", 60),
                ("Tipo", 38),
                ("Cant.", 18),
                ("Destino", 48),
            ],
            rows=[
                [
                    row["Date"].strftime("%d/%m/%Y") if row["Date"] else "-",
                    _truncate(row["ItemName"], 32),
                    movement_type_names.get(row["MovementTypeID"], "?"),
                    str(row["Quantity"]),
                    _truncate(row["Destination"], 26),
                ]
                for row in movimientos
            ],
            type_col_index=2,
        )
        if movimientos_count > 60:
            pdf.ln(3)
            pdf.set_font("Helvetica", "I", 7)
            pdf.set_text_color(*COLOR_TEXT_MUTED)
            pdf.cell(0, 4, f"Se muestran los 60 movimientos mas recientes de {movimientos_count} totales.", 0, 1)
    else:
        _draw_empty(pdf, "No hubo movimientos registrados en este periodo.")

    output = pdf.output(dest="S")
    if isinstance(output, str):
        return output.encode("latin-1")
    return bytes(output)

def _draw_table(pdf, headers, rows, critical_col_index=None,
                badge_col_index=None, type_col_index=None, total_row=None):
    """
    Tabla con header morado, filas zebra, padding generoso.
    critical_col_index: columna en rojo+bold (stock actual)
    badge_col_index: columna con badge rojo (déficit)
    type_col_index: columna de tipo de movimiento (color según entrada/salida)
    total_row: tupla (label, valor) para fila de totales al pie
    """
    # Header morado
    pdf.set_x(12)
    pdf.set_fill_color(*COLOR_PURPLE_DARK)
    pdf.set_text_color(*COLOR_WHITE)
    pdf.set_font("Helvetica", "B", 8)
    for i, (name, width) in enumerate(headers):
        align = "L" if i == 0 else "C"
        pdf.cell(width, 7, "  " + name if i == 0 else name, 0, 0, align, fill=True)
    pdf.ln()

    # Filas
    pdf.set_font("Helvetica", "", 8)
    zebra = False
    for row in rows:
        # Salto de página si se va a salir
        if pdf.get_y() > 255:
            pdf.add_page()
            pdf.set_x(12)
            pdf.set_fill_color(*COLOR_PURPLE_DARK)
            pdf.set_text_color(*COLOR_WHITE)
            pdf.set_font("Helvetica", "B", 8)
            for i, (name, width) in enumerate(headers):
                align = "L" if i == 0 else "C"
                pdf.cell(width, 7, "  " + name if i == 0 else name, 0, 0, align, fill=True)
            pdf.ln()
            pdf.set_font("Helvetica", "", 8)
            zebra = False

        pdf.set_x(12)
        if zebra:
            pdf.set_fill_color(250, 250, 250)
        else:
            pdf.set_fill_color(*COLOR_WHITE)
        # Pintar fondo de toda la fila primero
        total_width = sum(w for _, w in headers)
        pdf.cell(total_width, 6, "", 0, 0, "L", fill=True)
        pdf.set_x(12)

        for i, ((name, width), value) in enumerate(zip(headers, row)):
            align = "L" if i == 0 else "C"

            # Badge de déficit (rojo con fondo)
            if badge_col_index is not None and i == badge_col_index:
                # Pintar badge dentro de la celda
                badge_x = pdf.get_x() + (width / 2) - 8
                badge_y = pdf.get_y() + 1
                pdf.set_fill_color(*COLOR_RED_BG)
                pdf.rect(badge_x, badge_y, 16, 4, "F")
                pdf.set_xy(badge_x, badge_y)
                pdf.set_text_color(*COLOR_RED_DARK)
                pdf.set_font("Helvetica", "B", 7)
                pdf.cell(16, 4, value, 0, 0, "C")
                pdf.set_xy(12 + sum(w for _, w in headers[:i + 1]), badge_y - 1)
                pdf.set_font("Helvetica", "", 8)
                pdf.set_text_color(*COLOR_TEXT)
                continue

            # Tipo de movimiento con color
            if type_col_index is not None and i == type_col_index:
                if "Entrada" in value:
                    pdf.set_text_color(*COLOR_GREEN_DARK)
                elif "Salida" in value:
                    pdf.set_text_color(*COLOR_ORANGE_DARK)
                else:
                    pdf.set_text_color(*COLOR_TEXT_MUTED)
                pdf.set_font("Helvetica", "B", 7)
                pdf.cell(width, 6, value, 0, 0, align)
                pdf.set_font("Helvetica", "", 8)
                pdf.set_text_color(*COLOR_TEXT)
                continue

            # Columna crítica (rojo + bold)
            if critical_col_index is not None and i == critical_col_index:
                pdf.set_text_color(*COLOR_RED)
                pdf.set_font("Helvetica", "B", 8)
            else:
                pdf.set_text_color(*COLOR_TEXT)
                pdf.set_font("Helvetica", "", 8)

            text = "  " + value if i == 0 else value
            pdf.cell(width, 6, text, 0, 0, align)

        pdf.ln()
        zebra = not zebra

    # Fila de total al pie
    if total_row:
        label, valor = total_row
        pdf.set_x(12)
        pdf.set_fill_color(*COLOR_PURPLE_LIGHT)
        pdf.set_text_color(*COLOR_PURPLE_DARK)
        pdf.set_font("Helvetica", "B", 8)
        total_width = sum(w for _, w in headers)
        pdf.cell(total_width * 0.6, 7, "  " + label, 0, 0, "L", fill=True)
        pdf.cell(total_width * 0.4, 7, valor + "  ", 0, 0, "R", fill=True)
        pdf.ln()

    pdf.set_text_color(*COLOR_TEXT)


def _draw_empty(pdf, mensaje):
    """Mensaje cuando una sección no tiene datos."""
    pdf.set_x(12)
    pdf.set_fill_color(*COLOR_PURPLE_LIGHT)
    pdf.set_text_color(*COLOR_TEXT_MUTED)
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(186, 10, mensaje, 0, 1, "C", fill=True)


# === RUTAS ===

@reports_bp.route("/api/reports/stock-quincenal/pdf", methods=["GET"])
def reporte_stock_quincenal_pdf():
    """
    Genera el reporte quincenal en PDF.

    Parámetros opcionales:
        ?desde=YYYY-MM-DD  Fecha inicio del período (default: hoy - 15 días)
        ?hasta=YYYY-MM-DD  Fecha fin del período (default: hoy)
        ?token=XXX         Token simple para uso desde n8n sin sesión

    Si no se está autenticado vía sesión y no se pasa token válido,
    devuelve 401.
    """
    # Auth: aceptar sesión normal O token compartido para n8n
    # Auth: aceptar sesión normal O token en header para n8n
    import os
    api_token = os.environ.get("REPORTS_API_TOKEN", "")
    token_header = request.headers.get("Authorization", "")

    if "user" not in session and token_header != f"Bearer {api_token}":
        return jsonify({"error": "No autorizado"}), 401
    
    try:
        # Parsear parámetros de fecha
        desde_str = request.args.get("desde")
        hasta_str = request.args.get("hasta")

        if hasta_str:
            fecha_hasta = datetime.strptime(hasta_str, "%Y-%m-%d")
            fecha_hasta = fecha_hasta.replace(hour=23, minute=59, second=59)
        else:
            fecha_hasta = datetime.now().replace(hour=23, minute=59, second=59)

        if desde_str:
            fecha_desde = datetime.strptime(desde_str, "%Y-%m-%d")
            fecha_desde = fecha_desde.replace(hour=0, minute=0, second=0)
        else:
            fecha_desde = fecha_hasta - timedelta(days=14)
            fecha_desde = fecha_desde.replace(hour=0, minute=0, second=0)

        # Generar PDF
        pdf_bytes = _build_pdf(fecha_desde, fecha_hasta)

        # Nombre del archivo
        nombre = f"reporte_quincenal_{fecha_hasta.strftime('%Y-%m-%d')}.pdf"

        return send_file(
            BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=nombre,
        )

    except ValueError as e:
        return jsonify({"error": f"Formato de fecha invalido: {str(e)}"}), 400
    except Exception as e:
        print("Error en reporte_stock_quincenal_pdf:", str(e))
        return jsonify({"error": str(e)}), 500