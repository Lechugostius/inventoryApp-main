from .database import get_connection

def add_status(name: str, description: str = None):
    """Agrega un nuevo estado en la base de datos.
    args:
        name: str, nombre del estado.
        description: str, descripción del estado.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_add_status @Name=?, @Description=?", (name, description))
            response = conn.commit()
            return {"message": "Status added successfully", "response": response}
    except Exception as e:
        print("Error:", e)
        raise e

def get_all_statuses():
    """Obtiene todos los estados de la base de datos."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_get_statuses")
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print("Error:", e)
        raise e

def update_status(status_id: int, name: str = None, description: str = None):
    """Actualiza los datos de un estado en la base de datos.
    args:
        status_id: int, ID del estado.
        name: str, nombre del estado.
        description: str, descripción del estado.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_update_status @ID=?, @Name=?, @Description=?", 
                           (status_id, name, description))
            response = conn.commit()
            return {"message": "Status updated successfully", "response": response}
    except Exception as e:
        print("Error:", e)
        raise e

def delete_status(status_id: int):
    """Elimina un estado de la base de datos por su ID.
    args:
        status_id: int, ID del estado.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_delete_status @ID=?", (status_id,))
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            return None
    except Exception as e:
        print("Error:", e)
        raise e