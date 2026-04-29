from .database import get_connection

def add_item_owner(name: str, description: str = None):
    """Agrega un nuevo propietario de ítem.
    args:
        name: str, nombre del propietario.
        description: str, descripción del propietario."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_add_item_owner @Name=?, @Description=?", (name, description))
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            return None
    except Exception as e:
        print("Error:", e)
        raise e

def get_all_item_owners():
    """Obtiene todos los propietarios de ítems."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_get_item_owners")
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print("Error:", e)
        raise e

def get_item_owner_by_id(owner_id: int):
    """Obtiene un propietario de ítem por su ID.
    args:
        owner_id: int, ID del propietario."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_get_item_owner_by_id @ID=?", (owner_id,))
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            return None
    except Exception as e:
        print("Error:", e)
        raise e

def update_item_owner(owner_id: int, name: str = None, description: str = None):
    """Actualiza un propietario de ítem.
    args:
        owner_id: int, ID del propietario.
        name: str, nombre del propietario.
        description: str, descripción del propietario."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_update_item_owner @ID=?, @Name=?, @Description=?", (owner_id, name, description))
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            return None
    except Exception as e:
        print("Error:", e)
        raise e

def delete_item_owner(owner_id: int):
    """Elimina un propietario de ítem.
    args:
        owner_id: int, ID del propietario."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_delete_item_owner @ID=?", (owner_id,))
            conn.commit()
            return {"message": "ItemOwner deleted successfully"}
    except Exception as e:
        print("Error:", e)
        raise e
