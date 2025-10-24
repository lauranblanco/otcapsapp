import streamlit as st
from drive_connector import get_drive_service
from drive_utils import list_files_in_folder
import os

# Eliminar token viejo al iniciar
if os.path.exists("token.pkl"):
    os.remove("token.pkl")
    print("✅ Token viejo eliminado, se generará uno nuevo.")


st.set_page_config(page_title="Google Drive Viewer", layout="wide")

st.title("📂 Archivos en Google Drive")

try:
    service = get_drive_service()
    files = list_files_in_folder(service)

    if not files:
        st.warning("No se encontraron archivos en la carpeta especificada.")
    else:
        for f in files:
            st.write(f"**{f['name']}** — {f['mimeType']} — 📅 {f['modifiedTime']}")

except Exception as e:
    st.error(f"Ocurrió un error: {e}")

