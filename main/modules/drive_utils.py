import pandas as pd
from io import BytesIO
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from modules.drive_connector import get_drive_service

def list_folders_in_folder(service, folder_id):
    """Devuelve una lista de carpetas dentro de un folder específico."""
    query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(
        q=query,
        fields="files(id, name)"
    ).execute()
    return results.get("files", [])

def load_csv_from_drive(file_id):
    try:
        service = get_drive_service()
        request = service.files().get_media(fileId=file_id)
        fh = BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        fh.seek(0)
        df = pd.read_csv(fh)
        return df
    except Exception as e:
        print("Error cargando archivo:", e)
        return pd.DataFrame()
