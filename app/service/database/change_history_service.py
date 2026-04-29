from .database import get_connection

def get_all_change_history():
    """Obtiene el historial de cambios ejecutando el procedimiento almacenado."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_get_change_history")
            rows =  cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print("Error:", e)
        raise e