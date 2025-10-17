import os, json, pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials

load_dotenv("main/.env")

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
TOKEN_PATH = os.getenv("TOKEN_PATH")
CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")

def get_drive_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds_dict = json.loads(CREDENTIALS_JSON)
            with open("temp_credentials.json", "w") as f:
                json.dump(creds_dict, f)
            flow = InstalledAppFlow.from_client_secrets_file("temp_credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
            os.remove("temp_credentials.json")

        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)

    return build("drive", "v3", credentials=creds)


def connect_to_drive():
    """Conecta a Google Drive usando las credenciales del .env."""

    # Leer credenciales desde variable de entorno
    credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    token_path = os.getenv("TOKEN_PATH", "token.json")

    if not credentials_json:
        raise ValueError("No se encontró GOOGLE_CREDENTIALS_JSON en el archivo .env.")

    # Parsear el JSON del .env
    creds_data = json.loads(credentials_json)

    # Crear flujo OAuth (cliente web)
    flow = InstalledAppFlow.from_client_config(
        creds_data,
        scopes=["https://www.googleapis.com/auth/drive"]
    )

    creds = None
    # Si ya hay token, cargarlo
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path)

    # Si no hay credenciales válidas, abrir el flujo de autenticación
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = flow.run_local_server(port=0)
        # Guardar token
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    service = build("drive", "v3", credentials=creds)
    return service



