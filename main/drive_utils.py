import os
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
FOLDER_ID = os.getenv("FOLDER_ID")


def list_files_in_folder(service):
    """Devuelve una lista de archivos dentro del folder de Google Drive."""
    try:
        results = service.files().list(
            q=f"'{FOLDER_ID}' in parents and trashed = false",
            fields="files(id, name, mimeType, modifiedTime)",
        ).execute()
        return results.get("files", [])
    except HttpError as error:
        print(f"Error al listar archivos: {error}")
        return []

