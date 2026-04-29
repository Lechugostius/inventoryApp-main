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
    """Agrega un nuevo ítem con costo unitario y moneda.
    args:
        name: str, nombre del ítem.
        description: str, descripción del ítem.
        category_id: int, ID de la categoría del ítem.
        unique_identifier: str, identificador único del ítem.
        supplier_id: int, ID del proveedor del ítem.
        status_id: int, ID del estado del ítem.
        location: str, ubicación del ítem.
        stock: int, cantidad de stock del ítem.
        owner_id: int, ID del propietario del ítem.
        unit_cost: float, costo unitario del ítem.
        currency: str, moneda del costo (USD o CRC).
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "EXEC sp_add_item @Name=?, @Description=?, @CategoryID=?, @UniqueIdentifier=?, @SupplierID=?, @StatusID=?, @Location=?, @Stock=?, @OwnerID=?, @UnitCost=?, @Currency=?",
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
                    unit_cost,
                    currency,
                ),
            )
            
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            return None
    except Exception as e:
        print("Error:", e)
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
    """Actualiza un ítem incluyendo costo unitario y moneda.
    args:
        item_id: int, ID del ítem.
        name: str, nombre del ítem.
        description: str, descripción del ítem.
        category_id: int, ID de la categoría del ítem.
        unique_identifier: str, identificador único del ítem.
        supplier_id: int, ID del proveedor del ítem.
        status_id: int, ID del estado del ítem.
        location: str, ubicación del ítem.
        owner_id: int, ID del propietario del ítem.
        stock: int, cantidad de stock del ítem.
        unit_cost: float, costo unitario del ítem.
        currency: str, moneda del costo (USD o CRC).
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "EXEC sp_update_item @ID=?, @Name=?, @Description=?, @CategoryID=?, @UniqueIdentifier=?, @SupplierID=?, @StatusID=?, @Location=?, @OwnerID=?, @Stock=?, @UnitCost=?, @Currency=?",
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
                    unit_cost,
                    currency,
                ),
            )
            
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            return None
    except Exception as e:
        print("Error:", e)
        raise e


# Las demás funciones permanecen igual
def get_all_items():
    """Obtiene todos los ítems."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_get_items")
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    except Exception as e:
        print("Error:", e)
        raise e


def get_items_by_filters(
    name: str = None,
    category_id: int = None,
    supplier_id: int = None,
    status_id: int = None,
    owner_id: int = None,
):
    """Obtiene ítems filtrados por diferentes criterios opcionales."""
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
        print("Error:", e)
        raise e


def get_item_by_id(item_id: int):
    """Obtiene un ítem por su ID."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_get_item_by_id @ID=?", (item_id,))
            rows = cursor.fetchone()
            if rows:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, rows))
            return None
    except Exception as e:
        print("Error:", e)
        raise e


def delete_item(item_id: int):
    """Elimina un ítem."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_delete_item @ID=?", (item_id,))
            response = conn.commit()
            return {"message": "Item deleted successfully", "response": response}
    except Exception as e:
        print("Error:", e)
        raise e