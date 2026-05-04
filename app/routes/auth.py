from flask import Blueprint, redirect, url_for, session, request, current_app
from msal import ConfidentialClientApplication
from ..service.database.user_service import get_user_by_azure_id, add_user

auth_bp = Blueprint("auth", __name__)

def ensure_user_exists(azure_user_data):
    """
    Asegura que el usuario existe en la base de datos local.
    Si no existe, lo crea y retorna su ID.
    """
    try:
        print("Verificando usuario con datos:", azure_user_data)  # Debug
        
        # Obtener el usuario por su Azure ID (oid)
        azure_id = azure_user_data.get('oid')
        if not azure_id:
            print("No se encontró oid en los datos de Azure")
            return None
            
        existing_user = get_user_by_azure_id(azure_id)
        
        if existing_user:
            print("Usuario existente encontrado:", existing_user)  # Debug
            # Usuario existe, actualizar sesión con ID local
            azure_user_data['local_id'] = existing_user['ID']
            session['user'] = azure_user_data
            return existing_user['ID']
        
        print("Usuario no encontrado, creando nuevo usuario")  # Debug
        
        # Preparar datos del usuario
        name = azure_user_data.get('name')
        email = azure_user_data.get('preferred_username')
        w
        if not name or not email:
            print("Faltan datos necesarios del usuario")
            return None
        
        # Usuario no existe, crearlo
        new_user = add_user(
            name=name,
            email=email,
            role_id=1,  # Rol por defecto
            azure_user_id=azure_id
        )
        
        if new_user:
            print("Nuevo usuario creado:", new_user)  # Debug
            # Actualizar sesión con ID local
            azure_user_data['local_id'] = new_user['ID']
            session['user'] = azure_user_data
            return new_user['ID']
        
        print("Error: No se pudo crear el usuario")  # Debug
        return None
        
    except Exception as e:
        print(f"Error asegurando existencia del usuario: {str(e)}")
        return None  # Retornamos None en lugar de levantar la excepción

@auth_bp.route("/login")
def login():
    client = ConfidentialClientApplication(
        client_id=current_app.config["AZURE_CLIENT_ID"],
        client_credential=current_app.config["AZURE_CLIENT_SECRET"],
        authority=current_app.config["AZURE_AUTHORITY"]
    )

    auth_url = client.get_authorization_request_url(
        scopes=["User.Read"],
        redirect_uri=current_app.config["AZURE_REDIRECT_URI"]
    )

    return redirect(auth_url)

@auth_bp.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Error: no se recibió el código de autorización.", 400

    client = ConfidentialClientApplication(
        client_id=current_app.config["AZURE_CLIENT_ID"],
        client_credential=current_app.config["AZURE_CLIENT_SECRET"],
        authority=f"https://login.microsoftonline.com/{current_app.config['AZURE_TENANT_ID']}"
    )

    try:
        result = client.acquire_token_by_authorization_code(
            code,
            scopes=["User.Read"],
            redirect_uri=current_app.config["AZURE_REDIRECT_URI"]
        )
    except Exception as e:
        return f"Error al intercambiar el código por un token: {str(e)}", 400

    if "access_token" in result:
        # Guardar datos de Azure en la sesión
        azure_user_data = result["id_token_claims"]
        print("Datos del usuario de Azure recibidos:", azure_user_data)  # Debug
        
        # Asegurar que el usuario existe en nuestra base de datos
        try:
            local_user_id = ensure_user_exists(azure_user_data)
            if not local_user_id:
                return "Error: No se pudo crear o actualizar el usuario local", 400
            
            print("Usuario asegurado con ID local:", local_user_id)  # Debug
            return redirect(url_for("main.render_base"))
            
        except Exception as e:
            print(f"Error al asegurar usuario local: {str(e)}")
            return f"Error al procesar el usuario: {str(e)}", 400
    else:
        return "Error al obtener el token de acceso.", 400

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))