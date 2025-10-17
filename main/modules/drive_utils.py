from modules.drive_auth import connect_to_drive
from googleapiclient.http import MediaIoBaseDownload
import pandas as pd
import io

def list_files_in_folder(folder_id):
    service = connect_to_drive()
    query = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    return results.get("files", [])

def load_csv_from_drive(file_id):
    service = connect_to_drive()
    request = service.files().get_media(fileId=file_id)
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    file.seek(0)
    return pd.read_csv(file)
