import pyodbc
from config import DB_CONFIG


def get_connection():
    connection_string = f"DRIVER={{{DB_CONFIG['driver']}}};SERVER={DB_CONFIG['server']};DATABASE={DB_CONFIG['database']};UID={DB_CONFIG['username']};PWD={DB_CONFIG['password']}"
    return pyodbc.connect(connection_string)


def execute_query(query: str, params: tuple = None):
    """
    Ejecuta una consulta SELECT y retorna las filas como lista de diccionarios.
    args:
        query: str, consulta SQL.
        params: tuple, parámetros opcionales para la consulta.
    returns:
        list[dict] con los resultados, o lista vacía si no hay filas.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            rows = cursor.fetchall()
            if not rows:
                return []

            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print("Error en execute_query:", e)
        raise e


def execute_non_query(query: str, params: tuple = None):
    """
    Ejecuta una consulta INSERT/UPDATE/DELETE y retorna el número de filas afectadas.
    args:
        query: str, consulta SQL.
        params: tuple, parámetros opcionales para la consulta.
    returns:
        int, número de filas afectadas.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            affected = cursor.rowcount
            conn.commit()
            return affected
    except Exception as e:
        print("Error en execute_non_query:", e)
        raise e