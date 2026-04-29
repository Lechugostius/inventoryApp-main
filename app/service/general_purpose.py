from datetime import datetime
import uuid
from dotenv import load_dotenv
import os
from azure.storage.blob.aio import BlobServiceClient

load_dotenv()


async def upload_blob(file_name, content):
    try:
        # Obtener la fecha actual para la carpeta
        today = datetime.now().strftime("%Y/%m/%d")

        # Generar un sufijo único basado en un UUID
        unique_suffix = uuid.uuid4().hex[:8]  # Solo usar los primeros 8 caracteres
        file_name_parts = file_name.rsplit(".", 1)  # Dividir nombre y extensión
        uploaded_blob_name = "inventory_files"

        if len(file_name_parts) == 2:  # Si el archivo tiene extensión
            base_name, extension = file_name_parts
            blob_name = (
                f"{uploaded_blob_name}/{today}/{base_name}_{unique_suffix}.{extension}"
            )
        else:  # Si no tiene extensión
            blob_name = f"{uploaded_blob_name}/{today}/{file_name}_{unique_suffix}"

        blob_name = blob_name.replace(" ", "_")

        # 📌 Conectar con Azure Blob Storage
        async with BlobServiceClient(
            account_url=os.getenv("AZURE_BLOB_SAS_URL"),
            credential=os.getenv("AZURE_BLOB_SAS_TOKEN"),
        ) as blob_service_client:

            container_client = blob_service_client.get_container_client(
                "inventoryitems"
            )
            blob_client = container_client.get_blob_client(blob=blob_name)
            await blob_client.upload_blob(content, overwrite=True)

            print(f"Archivo subido a: {blob_name}")
            return blob_name

    except Exception as e:
        print(f"Error al subir el archivo '{file_name}': {str(e)}")
        return None
