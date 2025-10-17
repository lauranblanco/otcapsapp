import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def get_drive_service():
    """Devuelve un cliente autenticado de Google Drive usando una cuenta de servicio."""
    if not SERVICE_ACCOUNT_JSON:
        raise ValueError("No se encontró GOOGLE_SERVICE_ACCOUNT_JSON en las variables de entorno.")
    
    creds_info = json.loads(SERVICE_ACCOUNT_JSON)
    credentials = service_account.Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    service = build("drive", "v3", credentials=credentials)
    return service


