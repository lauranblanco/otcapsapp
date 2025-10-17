import streamlit as st
import os
from modules.drive_connector import connect_to_drive
from modules.drive_utils import list_folders_in_folder
from dotenv import load_dotenv
from pathlib import Path

# --- Cargar variables de entorno ---
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# --- Conexión con Google Drive ---
st.set_page_config(page_title="Google Drive Viewer", page_icon="📁", layout="wide")

st.title("📂 Visualizador de carpetas en Google Drive")

# Obtener ID de carpeta principal desde el .env
folder_id = os.getenv("FOLDER_ID")

if not folder_id:
    st.error("⚠️ No se encontró 'FOLDER_ID' en el archivo .env.")
    st.stop()

# Conectarse a Google Drive
with st.spinner("Conectando con Google Drive..."):
    try:
        service = connect_to_drive()
        st.success("✅ Conexión exitosa con Google Drive")
    except Exception as e:
        st.error(f"❌ Error al conectar con Google Drive: {e}")
        st.stop()

# --- Listar carpetas dentro del folder principal ---
st.subheader("📁 Carpetas dentro del folder principal")

try:
    folders = list_folders_in_folder(service, folder_id)
    if not folders:
        st.info("No se encontraron carpetas dentro del folder principal.")
    else:
        for folder in folders:
            st.write(f"📁 **{folder['name']}** — ID: `{folder['id']}`")
except Exception as e:
    st.error(f"Error al listar carpetas: {e}")

