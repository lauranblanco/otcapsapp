import os
import json
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials

# Cargar variables del .env (ruta absoluta para evitar fallos)
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
TOKEN_PATH = os.getenv("TOKEN_PATH")
CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")


def get_drive_service():
    """Devuelve un cliente autenticado para Google Drive."""
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



