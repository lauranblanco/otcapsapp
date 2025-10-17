import os
import json
import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from dotenv import load_dotenv

# --- Cargar variables de entorno ---
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
TOKEN_PATH = os.getenv("TOKEN_PATH")
CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")


def get_drive_service():
    """Devuelve un cliente autenticado para Google Drive."""
    creds = None

    # 1️⃣ Intentar cargar token si existe
    if TOKEN_PATH and os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

    # 2️⃣ Si no hay token válido, cargar desde .env
    if not creds or not creds.valid:
        if not CREDENTIALS_JSON:
            raise ValueError("No se encontró GOOGLE_CREDENTIALS_JSON en el archivo .env.")

        creds_dict = json.loads(CREDENTIALS_JSON)

        # Caso 1: formato OAuth (como el tuyo)
        if "web" in creds_dict:
            client_config = creds_dict["web"]
            creds = Credentials.from_authorized_user_info(client_config, scopes=SCOPES)
        # Caso 2: service account
        elif "type" in creds_dict and creds_dict["type"] == "service_account":
            creds = ServiceAccountCredentials.from_service_account_info(creds_dict, scopes=SCOPES)
        else:
            raise ValueError("El formato de GOOGLE_CREDENTIALS_JSON no es válido.")

        # Guardar token
        if TOKEN_PATH:
            with open(TOKEN_PATH, "wb") as token:
                pickle.dump(creds, token)

    # 3️⃣ Crear cliente de Drive
    service = build("drive", "v3", credentials=creds)
    return service



