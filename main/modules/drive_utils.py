import os
import sys

# Asegurar que el módulo pueda importar drive_connector sin importar desde dónde se ejecute
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from drive_connector import get_drive_service


def list_folders_in_folder(folder_id):
    """Devuelve las subcarpetas dentro de una carpeta de Drive."""
    service = get_drive_service()

    results = (
        service.files()
        .list(
            q=f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields="files(id, name)",
        )
        .execute()
    )

    folders = results.get("files", [])
    return folders

