from .database import get_connection

### 📂 Categories ###
def add_category(name: str):
    """Agrega una nueva categoría y devuelve la información insertada.
    
    Args:
        name (str): Nombre de la categoría.
    
    Returns:
        dict: Datos de la categoría recién creada.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_add_category @Name=?", (name,))
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            return None
    except Exception as e:
        print("Error:", e)
        raise e


def get_all_categories():
    """Obtiene todas las categorías."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_get_categories")
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print("Error:", e)
        raise e

def update_category(category_id: int, name: str = None):
    """Actualiza una categoría.
    args:
        category_id (int): ID de la categoría.
        name (str): Nombre de la categoría.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_update_category @ID=?, @Name=?", (category_id, name))
            response = conn.commit()
            return {"message": "Category updated successfully",
                    "response": response}   
    except Exception as e:
        print("Error:", e)
        raise e

def delete_category(category_id: int):
    """Elimina una categoría.
    args:
        category_id (int): ID de la categoría.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_delete_category @ID=?", (category_id,))
            response = conn.commit()
            return {"message": "Category deleted successfully",
                    "response": response}
    except Exception as e:
        print("Error:", e)
        raise e
