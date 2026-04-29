from .database import get_connection


def add_user(name: str, email: str, role_id: int = None, azure_user_id: str = None):
    """Agrega un nuevo usuario en la base de datos.
    args:
        name: str, nombre del usuario.
        email: str, correo electrónico del usuario.
        role_id: int, ID del rol del usuario.
        azure_user_id: str, ID del usuario en Azure
    """
    try:
        print(f"Intentando agregar usuario: {name}, {email}, {role_id}, {azure_user_id}")  # Debug
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_add_user @Name=?, @Email=?, @RoleID=?, @AzureUserID=?", 
                           (name, email, role_id, azure_user_id))
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                result = dict(zip(columns, row))
                print(f"Usuario agregado exitosamente: {result}")  # Debug
                return result
            print("No se obtuvieron resultados al agregar usuario")  # Debug
            return None
    except Exception as e:
        print(f"Error agregando usuario: {str(e)}")
        return None  # Retornamos None en lugar de levantar la excepción

def get_all_users():
    """Obtiene todos los usuarios de la base de datos."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_get_users")
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print("Error:", e)
        raise e

def get_user_by_id(user_id: int):
    """Obtiene un usuario por su ID.
    args:
        user_id: int, ID del usuario.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_get_user_by_id @ID=?", (user_id,))
            rows =  cursor.fetchone()  # Devuelve solo un resultado
            columns = [column[0] for column in cursor.description]
            return dict(zip(columns, rows))
    except Exception as e:
        print("Error:", e)
        raise e

def get_user_by_azure_id(azure_user_id: str):
    """Obtiene un usuario por su AzureUserID.
    args:
        azure_user_id: str, ID del usuario en Azure.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_get_user_by_azure_id @AzureUserID=?", (azure_user_id,))
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            print(f"No se encontró usuario con Azure ID: {azure_user_id}")  # Debug
            return None
    except Exception as e:
        print(f"Error buscando usuario por Azure ID: {str(e)}")
        return None  # Retornamos None en lugar de levantar la excepción

def update_user(user_id: int, name: str = None, email: str = None, role_id: int = None, azure_user_id: str = None):
    """Actualiza los datos de un usuario en la base de datos.
    args:
        user_id: int, ID del usuario.
        name: str, nombre del usuario.
        email: str, correo electrónico del usuario.
        role_id: int, ID del rol del usuario.
        azure_user_id: str, ID del usuario en Azure.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_update_user @ID=?, @Name=?, @Email=?, @RoleID=?, @AzureUserID=?", 
                           (user_id, name, email, role_id, azure_user_id))
            response = conn.commit()
            return {"message": "User updated successfully", "response": response}
    except Exception as e:
        print("Error:", e)
        raise e

def delete_user(user_id: int):
    """Elimina un usuario de la base de datos por su ID.
    args:
        user_id: int, ID del usuario.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_delete_user @ID=?", (user_id,))
            response = conn.commit()
            return {"message": "User deleted successfully", "response": response}
    except Exception as e:
        print("Error:", e)
        raise e