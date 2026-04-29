from app.service.database.category_service import add_category, get_all_categories, update_category, delete_category
from app.service.database.change_history_service import get_all_change_history
from app.service.database.files_service import add_file, get_files_by_item_id, update_file, delete_file
from app.service.database.items_service import add_item, get_all_items, get_item_by_id, update_item, delete_item, get_items_by_filters
from app.service.database.movement_service import add_movement, get_all_movements, update_movement, delete_movement
from app.service.database.movement_types_service import add_movement_type, get_all_movement_types, update_movement_type, delete_movement_type
from app.service.database.roles_service import add_role, get_all_roles, update_role, delete_role
from app.service.database.suppliers_service import add_supplier, get_all_suppliers, update_supplier, delete_supplier
from app.service.database.user_service import add_user, get_all_users, get_user_by_id, update_user, delete_user
from app.service.database.item_owner_service import add_item_owner, get_all_item_owners, get_item_owner_by_id, update_item_owner, delete_item_owner

def test_category_service():
    """Pruebas para el servicio de categorías."""
    print("Testing category service...")
    print("Adding category...")
    add_category_response = add_category("Test category")
    print(f"Category added: {add_category_response}")
    print("Getting all categories...")
    categories = get_all_categories()
    print(f"Categories: {categories}")
    print("Updating category...")
    update_category_response = update_category(1, "Updated test category")
    print(f"Category updated: {update_category_response}")
    print("Deleting category...")
    delete_category_response = delete_category(add_category_response["ID"])
    print(f"Category deleted: {delete_category_response}")
    print("Category service test finished.")

def test_history_service():
    """Pruebas para el servicio de historial."""
    print("Testing history service...")
    print("Getting all change history...")
    history = get_all_change_history()
    print(f"Change history: {history}")
    print("History service test finished.")

def test_files_service():
    """Pruebas para el servicio de archivos."""
    print("Testing files service...")
    print("Adding file...")
    add_file_response = add_file(1, "test_file.txt", "image/png")
    print(f"File added: {add_file_response}")
    print("Getting files by item id...")
    files = get_files_by_item_id(add_file_response["ItemID"])
    print(f"Files: {files}")
    print("Updating file...")
    update_file_response = update_file(1, 1, "updated_test_file.txt", "image/jpeg")
    print(f"File updated: {update_file_response}")
    print("Deleting file...")
    delete_file_response = delete_file(add_file_response["ID"])
    print(f"File deleted: {delete_file_response}")
    print("Files service test finished.")

def test_items_service():
    """Pruebas para el servicio de items."""
    print("Testing items service...")
    print("Adding item...")
    add_item_response = add_item("Test item", "Test description", 1, "Test unique identifier 2", 1, 1, "Test location", 2)
    print(f"Item added: {add_item_response}")
    print("Getting all items...")
    items = get_all_items()
    print(f"Items: {items}")
    print("Getting item by ID...")
    item = get_item_by_id(add_item_response["ID"])
    print(f"Item: {item}")
    print("Updating item...")
    update_item_response = update_item(add_item_response["ID"], "Updated test item", "Updated test description", 2, "Updated test unique identifier", 2, 2, "Updated test location", 3, 10)
    print(f"Item updated: {update_item_response}")
    print("Deleting item...")
    delete_item_response = delete_item(add_item_response["ID"])
    print(f"Item deleted: {delete_item_response}")
    print("Getting items by filters...")
    items = get_items_by_filters(name="Test item", category_id=1, status_id=1, owner_id=1)
    print(f"Items filtered: {items}")
    print("Items service test finished.")


def test_item_owners_service():
    """Pruebas para el servicio de propietarios de ítems."""
    print("Testing ItemOwners service...")
    
    print("Adding ItemOwner...")
    add_owner_response = add_item_owner("IT Department", "Responsible for IT assets")
    print(f"ItemOwner added: {add_owner_response}")

    print("Getting all ItemOwners...")
    owners = get_all_item_owners()
    print(f"ItemOwners: {owners}")

    print("Getting ItemOwner by ID...")
    owner = get_item_owner_by_id(add_owner_response["ID"])
    print(f"ItemOwner: {owner}")

    print("Updating ItemOwner...")
    update_owner_response = update_item_owner(add_owner_response["ID"], "Updated IT Department", "Updated description")
    print(f"ItemOwner updated: {update_owner_response}")

    print("Deleting ItemOwner...")
    delete_owner_response = delete_item_owner(add_owner_response["ID"])
    print(f"ItemOwner deleted: {delete_owner_response}")

    print("ItemOwners service test finished.")


def test_movement_services():
    """Pruebas para el servicio de movimientos."""
    print("Testing movement services...")
    print("Adding movement...")
    add_movement_response = add_movement(1, 1, 1, 1, 1, "Test destination", "Test notes")
    print(f"Movement added: {add_movement_response}")
    print("Getting all movements...")
    movements = get_all_movements()
    print(f"Movements: {movements}")
    print("Updating movement...")
    update_movement_response = update_movement(add_movement_response["ID"], 1, 2, 2, 2, 2, "Updated test destination", "Updated test notes")
    print(f"Movement updated: {update_movement_response}")
    print("Deleting movement...")
    delete_movement_response = delete_movement(add_movement_response["ID"])
    print(f"Movement deleted: {delete_movement_response}")
    print("Movement services test finished.")

def test_movement_types_service():
    """Pruebas para el servicio de tipos de movimientos."""
    print("Testing movement types service...")
    print("Adding movement type...")
    add_movement_type_response = add_movement_type("Test movement type")
    print(f"Movement type added: {add_movement_type_response}")
    print("Getting all movement types...")
    movement_types = get_all_movement_types()
    print(f"Movement types: {movement_types}")
    print("Updating movement type...")
    update_movement_type_response = update_movement_type(add_movement_type_response["ID"], "Updated test movement type")
    print(f"Movement type updated: {update_movement_type_response}")
    print("Deleting movement type...")
    delete_movement_type_response = delete_movement_type(add_movement_type_response["ID"])
    print(f"Movement type deleted: {delete_movement_type_response}")
    print("Movement types service test finished.")
    
def test_roles_service():
    """Pruebas para el servicio de roles."""
    print("Testing roles service...")
    print("Adding role...")
    add_role_response = add_role("Test role","test description")
    print(f"Role added: {add_role_response}")
    print("Getting all roles...")
    roles = get_all_roles()
    print(f"Roles: {roles}")
    print("Updating role...")
    update_role_response = update_role(add_role_response["ID"], description="Updated test role")
    print(f"Role updated: {update_role_response}")
    print("Deleting role...")
    delete_role_response = delete_role(add_role_response["ID"])
    print(f"Role deleted: {delete_role_response}")
    print("Roles service test finished.")
    
def test_suppliers_service():
    """Pruebas para el servicio de proveedores."""
    print("Testing suppliers service...")
    print("Adding supplier...")
    add_supplier_response = add_supplier("Test supplier", "Test contact", "1234567890", "a@s", "Test address", "Test notes")
    print(f"Supplier added: {add_supplier_response}")
    print("Getting all suppliers...")
    suppliers = get_all_suppliers()
    print(f"Suppliers: {suppliers}")
    print("Updating supplier...")
    update_supplier_response = update_supplier(add_supplier_response["ID"], "Updated test supplier", "Updated test contact", "0987654321", "b@s", "Updated test address", "Updated test notes")
    print(f"Supplier updated: {update_supplier_response}")
    print("Deleting supplier...")
    delete_supplier_response = delete_supplier(add_supplier_response["ID"])
    print(f"Supplier deleted: {delete_supplier_response}")
    print("Suppliers service test finished.")

def test_user_service():
    """Pruebas para el servicio de usuarios."""
    print("Testing user service...")
    print("Adding user...")
    add_user_response = add_user(name="Test user", email="ca@s", role_id=1, azure_user_id= "1")
    print(f"User added: {add_user_response}")
    print("Getting all users...")
    users = get_all_users()
    print(f"Users: {users}")
    print("Getting user by ID...")
    user = get_user_by_id(add_user_response["ID"])
    print(f"User: {user}")
    print("Updating user...")
    update_user_response = update_user(add_user_response["ID"], "Updated test user", "va@s", 2, "2")
    print(f"User updated: {update_user_response}")
    print("Deleting user...")
    delete_user_response = delete_user(add_user_response["ID"])
    print(f"User deleted: {delete_user_response}")
    print("User service test finished.")

def test_all_services():
    """Pruebas para todos los servicios."""
    try:
        test_category_service()
        test_history_service()
        test_files_service()
        test_items_service()
        test_item_owners_service()
        test_movement_services()
        test_movement_types_service()
        test_roles_service()
        test_suppliers_service()
        test_user_service()
    except Exception as e:
        print("Error:", e)
    print("All services tests finished.")

test_all_services()