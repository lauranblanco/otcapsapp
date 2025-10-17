import os
import sys
from googleapiclient.errors import HttpError

# Asegurar que el módulo pueda importar drive_connector
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from drive_connector import get_drive_service


def list_folders_in_folder(folder_id: str):
    """Lista solo las carpetas dentro de un folder de Drive."""
    try:
        service = get_drive_service()

        query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(
            q=query,
            spaces='drive',
            fields="files(id, name)"
        ).execute()

        folders = results.get("files", [])
        return folders

    except HttpError as error:
        print(f"Ocurrió un error: {error}")
        return []

