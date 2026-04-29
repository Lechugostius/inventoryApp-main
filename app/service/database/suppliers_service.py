from .database import get_connection

### 📂 Suppliers ###
def add_supplier(name: str, contact: str = None, phone: str = None, email: str = None, address: str = None, notes: str = None):
    """Agrega un nuevo proveedor.
    args:
        name: str, nombre del proveedor.
        contact: str, persona de contacto.
        phone: str, teléfono de contacto.
        email: str, correo electrónico de contacto.
        address: str, dirección del proveedor.
        notes: str, notas adicionales.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_add_supplier @Name=?, @Contact=?, @Phone=?, @Email=?, @Address=?, @Notes=?", 
                           (name, contact, phone, email, address, notes))
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            return None
    except Exception as e:
        print("Error:", e)
        raise e

def get_all_suppliers():
    """Obtiene todos los proveedores."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_get_suppliers")
            rows = cursor.fetchall()  # ← CORRECCIÓN: Cambié esta línea
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]  # ← CORRECCIÓN: Agregué esta línea
    except Exception as e:
        print("Error:", e)
        raise e

def update_supplier(supplier_id: int, name: str = None, contact: str = None, phone: str = None, email: str = None, address: str = None, notes: str = None):
    """Actualiza un proveedor.
    args:
        supplier_id: int, ID del proveedor.
        name: str, nombre del proveedor.
        contact: str, persona de contacto.
        phone: str, teléfono de contacto.
        email: str, correo electrónico de contacto.
        address: str, dirección del proveedor.
        notes: str, notas adicion
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_update_supplier @ID=?, @Name=?, @Contact=?, @Phone=?, @Email=?, @Address=?, @Notes=?", 
                           (supplier_id, name, contact, phone, email, address, notes))
            response = conn.commit()
            return {"message": "Supplier updated successfully", "response": response}
    except Exception as e:
        print("Error:", e)
        raise e

def delete_supplier(supplier_id: int):
    """Elimina un proveedor.
    args:
        supplier_id: int, ID del proveedor.
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_delete_supplier @ID=?", (supplier_id,))
            response = conn.commit()
            return {"message": "Supplier deleted successfully", "response": response}
    except Exception as e:
        print("Error:", e)
        raise e