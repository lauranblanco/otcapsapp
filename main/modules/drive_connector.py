import os
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv
from pathlib import Path

# Cargar .env de forma robusta
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def connect_to_drive():
    """Conecta a Google Drive usando el JSON del .env (sin archivos extras)."""
    credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    token_path = os.getenv("TOKEN_PATH", "token.json")

    if not credentials_json:
        raise ValueError("No se encontró GOOGLE_CREDENTIALS_JSON en el archivo .env")

    creds = None

    # Cargar token si ya existe
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # Si no hay credenciales válidas, iniciar flujo OAuth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds_dict = json.loads(credentials_json)
            flow = InstalledAppFlow.from_client_config(creds_dict, SCOPES)
            creds = flow.run_local_server(port=0)
        # Guardar token
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return build("drive", "v3", credentials=creds)



