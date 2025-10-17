import os
import json
import pickle
import streamlit as st
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv

# --- Cargar variables de entorno (solo si existe .env local) ---
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

# --- Variables de configuración ---
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# Si estás local: usar variables del .env
TOKEN_PATH = os.getenv("TOKEN_PATH", "token.pkl")
CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")

# Si estás en Streamlit Cloud: usar secrets
if not CREDENTIALS_JSON and "GOOGLE_CREDENTIALS_JSON" in st.secrets:
    CREDENTIALS_JSON = st.secrets["GOOGLE_CREDENTIALS_JSON"]
if "TOKEN_PATH" in st.secrets:
    TOKEN_PATH = st.secrets["TOKEN_PATH"]

def get_drive_service():
    """Devuelve un cliente autenticado para Google Drive."""
    creds = None

    # Cargar token si existe
    if TOKEN_PATH and os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)

    # Si no hay credenciales válidas, autenticarse
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_JSON:
                raise ValueError("No se encontró GOOGLE_CREDENTIALS_JSON ni en .env ni en st.secrets.")

            creds_dict = json.loads(CREDENTIALS_JSON)

            # Guardar temporalmente el JSON para usarlo con InstalledAppFlow
            with open("temp_credentials.json", "w") as f:
                json.dump(creds_dict, f)

            flow = InstalledAppFlow.from_client_secrets_file("temp_credentials.json", SCOPES)

            try:
                # 🔹 Intentar flujo local (solo si hay navegador)
                creds = flow.run_local_server(port=0)
            except Exception:
                # 🔹 Si no hay navegador (por ejemplo, en Streamlit Cloud), usar modo consola
                print("⚠️ No se pudo abrir el navegador; usando flujo de consola.")
                creds = flow.run_console()

            os.remove("temp_credentials.json")

        # Guardar token actualizado
        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)

    return build("drive", "v3", credentials=creds)



