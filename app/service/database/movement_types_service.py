from .database import get_connection

### 📂 MovementTypes ###

def add_movement_type(name: str, description: str = None):
    """Agrega un nuevo tipo de movimiento.
    args:
        name: str, nombre del tipo de movimiento.
        description: str, descripción del tipo de movimiento.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_add_movement_type @Name=?, @Description=?", (name, description))
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            return None
    except Exception as e:
        print("Error:", e)
        raise e

def get_all_movement_types():
    """Obtiene todos los tipos de movimiento."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_get_movement_types")
            rows =  cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print("Error:", e)
        raise e

def update_movement_type(movement_type_id: int, name: str = None, description: str = None):
    """Actualiza un tipo de movimiento.
    args:
        movement_type_id: int, ID del tipo de movimiento.
        name: str, nombre del tipo de movimiento.
        description: str, descripción del tipo de movimiento.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_update_movement_type @ID=?, @Name=?, @Description=?", (movement_type_id, name, description))
            response = conn.commit()
            return {"message": "Movement type updated successfully", "response": response}
    except Exception as e:
        print("Error:", e)
        raise e

def delete_movement_type(movement_type_id: int):
    """Elimina un tipo de movimiento.
    args:
        movement_type_id: int, ID del tipo de movimiento.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_delete_movement_type @ID=?", (movement_type_id,))
            response = conn.commit()
            return {"message": "Movement type deleted successfully", "response": response}
    except Exception as e:
        print("Error:", e)
        raise e
