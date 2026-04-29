from .database import get_connection

def add_file(item_id: int, url: str, file_type: str):
    """Agrega un archivo asociado a un ítem.
    args:
        item_id (int): ID del ítem.
        url (str): URL del archivo.
        file_type (str): Tipo de archivo
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_add_file @ItemID=?, @URL=?, @Type=?", (item_id, url, file_type))
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            return None
    except Exception as e:
        print("Error:", e)
        raise e

def update_file(file_id: int, item_id: int = None, url: str = None, file_type: str = None):
    """Actualiza un archivo.
    args:
        file_id (int): ID del archivo.
        item_id (int): ID del ítem.
        url (str): URL del archivo.
        file_type (str): Tipo de archivo
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_update_file @ID=?, @ItemID=?, @URL=?, @Type=?", (file_id, item_id, url, file_type))
            response = conn.commit()
            return {"message": "File updated successfully", "response": response}
    except Exception as e:
        print("Error:", e)
        raise e

def delete_file(file_id: int):
    """Elimina un archivo.
    args:
        file_id (int): ID del archivo.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_delete_file @ID=?", (file_id,))
            response = conn.commit()
            return {"message": "File deleted successfully", "response": response}
    except Exception as e:
        print("Error:", e)
        raise e
    
def get_files_by_item_id(item_id: int):
    """Obtiene todos los archivos asociados a un ItemID.
    args:
        item_id (int): ID del ítem.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_get_files_by_item_id @ItemID=?", (item_id,))
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print("Error:", e)
        raise e
