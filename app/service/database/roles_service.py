from .database import get_connection

### 📂 Roles ###
def add_role(name: str, description: str = None):
    """Agrega un nuevo rol en la base de datos.
    args:
        name: str, nombre del rol.
        description: str, descripción del rol.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_add_role @Name=?, @Description=?", (name, description))
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            return None
    except Exception as e:
        print("Error:", e)
        raise e

def get_all_roles():
    """Obtiene todos los roles."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_get_roles")
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print("Error:", e)
        raise e

def update_role(role_id: int, name: str = None, description: str = None):
    """Actualiza un rol en la base de datos.
    args:
        role_id: int, ID del rol.
        name: str, nombre del rol.
        description: str, descripción del rol.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_update_role @ID=?, @Name=?, @Description=?", (role_id, name, description))
            response = conn.commit()
            return {"message": "Role updated successfully", "response": response}
    except Exception as e:
        print("Error:", e)
        raise e

def delete_role(role_id: int):
    """Elimina un rol de la base de datos.
    args:
        role_id: int, ID del rol.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_delete_role @ID=?", (role_id,))
            response = conn.commit()
            return {"message": "Role deleted successfully", "response": response}
    except Exception as e:
        print("Error:", e)
        raise e
