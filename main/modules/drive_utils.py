import pandas as pd
from io import BytesIO
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from modules.drive_connector import get_drive_service

def list_files_in_folder(folder_id):
    try:
        service = get_drive_service()
        results = service.files().list(
            q=f"'{folder_id}' in parents and mimeType='text/csv'",
            fields="files(id, name)"
        ).execute()
        return results.get("files", [])
    except HttpError as error:
        print(f"Ocurrió un error: {error}")
        return []

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
