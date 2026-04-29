from .database import get_connection

def get_all_paises():
    """Obtiene todos los países."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id_pais, nombre, codigo FROM dbo.Paises ORDER BY nombre")
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print("Error:", e)
        raise e

def get_pais_by_id(pais_id: int):
    """Obtiene un país por su ID."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id_pais, nombre, codigo FROM dbo.Paises WHERE id_pais = ?", (pais_id,))
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            return None
    except Exception as e:
        print("Error:", e)
        raise e