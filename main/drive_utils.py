import os
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (opcional)
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
FOLDER_ID = os.getenv("FOLDER_ID")  # solo si quieres mantener compatibilidad

def list_files_in_folder(service, folder_id=None):
    """
    Devuelve una lista de archivos dentro de una carpeta específica de Google Drive.
    Si no se pasa folder_id, usa el FOLDER_ID definido en .env.
    """
    folder_id = folder_id or FOLDER_ID
    if not folder_id:
        raise ValueError("No se proporcionó un folder_id y no hay FOLDER_ID en .env")

    try:
        query = f"'{folder_id}' in parents and trashed = false"
        results = service.files().list(
            q=query,
            fields="files(id, name, mimeType, modifiedTime)"
        ).execute()
        return results.get("files", [])
    except HttpError as error:
        print(f"Error al listar archivos: {error}")
        return []


def list_folders_in_folder(service, folder_id=None):
    """
    Devuelve solo las subcarpetas dentro de una carpeta.
    Si no se pasa folder_id, usa el FOLDER_ID definido en .env.
    """
    folder_id = folder_id or FOLDER_ID
    if not folder_id:
        raise ValueError("No se proporcionó un folder_id y no hay FOLDER_ID en .env")

    try:
        query = f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = service.files().list(
            q=query,
            fields="files(id, name, mimeType, modifiedTime)"
        ).execute()
        return results.get("files", [])
    except HttpError as error:
        print(f"Error al listar carpetas: {error}")
        return []

