from .database import get_connection

### 📂 Movements ###
def add_movement(item_id: int, movement_type_id: int, quantity: int, origin_user_id: int, responsible_user_id: int, destination: str = None, notes: str = None):
    """Agrega un nuevo movimiento y actualiza el stock del item.
    args:
        item_id: int, ID del ítem.
        movement_type_id: int, ID del tipo de movimiento.
        quantity: int, cantidad del movimiento.
        origin_user_id: int, ID del usuario de origen.
        responsible_user_id: int, ID del usuario responsable.
        destination: str, destino del movimiento.
        notes: str, notas del movimiento
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # 1. Obtener el item actual y su stock
            cursor.execute("SELECT Stock FROM Items WHERE ID = ?", (item_id,))
            result = cursor.fetchone()
            current_stock = result[0] if result and result[0] is not None else 0
            
            print(f"Stock actual del item {item_id}: {current_stock}")  # Debug
            
            # 2. Calcular nuevo stock basado en el tipo de movimiento
            new_stock = current_stock
            if movement_type_id == 1:  # Salida (Check-Out)
                if current_stock < quantity:
                    raise ValueError(f"Stock insuficiente. Stock actual: {current_stock}, Cantidad solicitada: {quantity}")
                new_stock = current_stock - quantity
            elif movement_type_id == 2:  # Entrada (Return)
                new_stock = current_stock + quantity
            
            print(f"Nuevo stock calculado: {new_stock}")  # Debug
            
            # 3. Actualizar el stock del item
            cursor.execute("UPDATE Items SET Stock = ? WHERE ID = ?", (new_stock, item_id))
            
            # 4. Registrar el movimiento
            cursor.execute("""
                INSERT INTO Movements (ItemID, MovementTypeID, Quantity, OriginUserID, ResponsibleUserID, Destination, Notes)
                OUTPUT INSERTED.ID, INSERTED.ItemID, INSERTED.MovementTypeID, INSERTED.Quantity, 
                       INSERTED.Date, INSERTED.OriginUserID, INSERTED.ResponsibleUserID, 
                       INSERTED.Destination, INSERTED.Notes
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (item_id, movement_type_id, quantity, origin_user_id, responsible_user_id, 
                  destination or 'Not specified', notes or 'No notes'))
            
            row = cursor.fetchone()
            
            # 5. Confirmar las transacciones
            conn.commit()
            
            print(f"Movimiento registrado y stock actualizado. Nuevo stock: {new_stock}")  # Debug
            
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            return None
            
    except Exception as e:
        print(f"Error en add_movement: {str(e)}")
        conn.rollback()  # Revertir cambios en caso de error
        raise e

def get_all_movements():
    """Obtiene todos los movimientos."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_get_movements")
            rows =  cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print("Error:", e)
        raise e

def update_movement(movement_id: int, item_id: int = None, movement_type_id: int = None, quantity: int = None, origin_user_id: int = None, responsible_user_id: int = None, destination: str = None, notes: str = None):
    """Actualiza un movimiento.
    args:
        movement_id: int, ID del movimiento.
        item_id: int, ID del ítem.
        movement_type_id: int, ID del tipo de movimiento.
        quantity: int, cantidad del movimiento.
        origin_user_id: int, ID del usuario de origen.
        responsible_user_id: int, ID del usuario responsable.
        destination: str, destino del movimiento.
        notes: str, notas del movimiento
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_update_movement @ID=?, @ItemID=?, @MovementTypeID=?, @Quantity=?, @OriginUserID=?, @ResponsibleUserID=?, @Destination=?, @Notes=?", 
                           (movement_id, item_id, movement_type_id, quantity, origin_user_id, responsible_user_id, destination, notes))
            response = conn.commit()
            return {"message": "Movement updated successfully", "response": response}
    except Exception as e:
        print("Error:", e)
        raise e

def delete_movement(movement_id: int):
    """Elimina un movimiento.
    args:
        movement_id: int, ID del movimiento
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("EXEC sp_delete_movement @ID=?", (movement_id,))
            response = conn.commit()
            return {"message": "Movement deleted successfully", "response": response}
    except Exception as e:
        print("Error:", e)
        raise e