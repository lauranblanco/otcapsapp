import os
import json
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
import streamlit as st

# --- Cargar variables de entorno ---
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
TOKEN_PATH = os.getenv("TOKEN_PATH")
CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")


def get_drive_service():
    """Devuelve un cliente autenticado para Google Drive (compatible con Streamlit)."""
    creds = None

    # 1️⃣ Cargar token si existe
    if TOKEN_PATH and os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)

    # 2️⃣ Si no hay credenciales válidas, iniciar autenticación
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_JSON:
                raise ValueError("No se encontró GOOGLE_CREDENTIALS_JSON en el entorno ni en secrets.")

            creds_dict = json.loads(CREDENTIALS_JSON)
            with open("temp_credentials.json", "w") as f:
                json.dump(creds_dict, f)

            flow = InstalledAppFlow.from_client_secrets_file("temp_credentials.json", SCOPES)

            try:
                # 🔹 Intentar abrir navegador local
                creds = flow.run_local_server(port=0)
            except Exception:
                # 🔹 Si falla (por ejemplo, en Streamlit Cloud)
                auth_url, _ = flow.authorization_url(prompt='consent')

                st.warning("Por favor, autentícate con Google para continuar.")
                st.write("👉 [Haz clic aquí para autorizar el acceso](" + auth_url + ")")

                auth_code = st.text_input("Pega aquí el código de autorización:")
                if st.button("Enviar código"):
                    try:
                        flow.fetch_token(code=auth_code)
                        creds = flow.credentials
                        with open(TOKEN_PATH, "wb") as token:
                            pickle.dump(creds, token)
                        st.success("✅ Autenticación completada con éxito.")
                    except Exception as e:
                        st.error(f"Error al obtener el token: {e}")
                        return None

            os.remove("temp_credentials.json")

        # 3️⃣ Guardar token
        if creds:
            with open(TOKEN_PATH, "wb") as token:
                pickle.dump(creds, token)
        else:
            raise ValueError("No se pudieron obtener credenciales válidas.")

    return build("drive", "v3", credentials=creds)


