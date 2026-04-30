from .database import get_connection

### 📂 Items ###

def add_item(
    name: str,
    description: str = None,
    category_id: int = None,
    unique_identifier: str = None,
    supplier_id: int = None,
    status_id: int = None,
    location: str = None,
    stock: str = None,
    owner_id: int = None,
    unit_cost: float = None,
    currency: str = "USD",
):
    """
    Agrega un nuevo item.
    Nota: unit_cost y currency se ignoran (no existen en la tabla Items).
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Los parámetros deben coincidir EXACTAMENTE con el SP
            cursor.execute(
                "EXEC sp_add_item @Name=?, @Description=?, @CategoryID=?, @UniqueIdentifier=?, @SupplierID=?, @StatusID=?, @Location=?, @Stock=?, @OwnerID=?",
                (
                    name,
                    description,
                    category_id,
                    unique_identifier,
                    supplier_id,
                    status_id,
                    location,
                    stock,
                    owner_id,
                ),
            )
            
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            return None
    except Exception as e:
        print("Error en add_item:", e)
        raise e


def update_item(
    item_id: int,
    name: str = None,
    description: str = None,
    category_id: int = None,
    unique_identifier: str = None,
    supplier_id: int = None,
    status_id: int = None,
    location: str = None,
    owner_id: int = None,
    stock: int = None,
    unit_cost: float = None,
    currency: str = None,
):
    """
    Actualiza un item.
    Nota: unit_cost y currency se ignoran (no existen en la tabla Items).
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "EXEC sp_update_item @ID=?, @Name=?, @Description=?, @CategoryID=?, @UniqueIdentifier=?, @SupplierID=?, @StatusID=?, @Location=?, @OwnerID=?, @Stock=?",
                (
                    item_id,
                    name,
                    description,
                    category_id,
                    unique_identifier,
                    supplier_id,
                    status_id,
                    location,
                    owner_id,
                    stock,
                ),
            )
            
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            return None
    except Exception as e:
        print("Error en update_item:", e)
        raise e


def get_all_items():
    """Obtiene todos los items."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_get_items")
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print("Error en get_all_items:", e)
        raise e


def get_items_by_filters(
    name: str = None,
    category_id: int = None,
    supplier_id: int = None,
    status_id: int = None,
    owner_id: int = None,
):
    """Obtiene items filtrados por diferentes criterios opcionales."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "EXEC sp_get_items_by_filters @Name=?, @CategoryID=?, @SupplierID=?, @StatusID=?, @OwnerID=?",
                (name, category_id, supplier_id, status_id, owner_id),
            )
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print("Error en get_items_by_filters:", e)
        raise e


def get_item_by_id(item_id: int):
    """Obtiene un item por su ID."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_get_item_by_id @ID=?", (item_id,))
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            return None
    except Exception as e:
        print("Error en get_item_by_id:", e)
        raise e


def delete_item(item_id: int):
    """Elimina un item."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_delete_item @ID=?", (item_id,))
            conn.commit()
            return {"message": "Item deleted successfully"}
    except Exception as e:
        print("Error en delete_item:", e)
        raise e