import os
import sys
import streamlit as st
from dotenv import load_dotenv

# --- Ajustar el path para encontrar los módulos ---
current_dir = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.join(current_dir, "modules")
if modules_path not in sys.path:
    sys.path.append(modules_path)

from drive_utils import list_folders_in_folder

# --- Cargar variables de entorno ---
load_dotenv(os.path.join(current_dir, ".env"))
FOLDER_ID = os.getenv("FOLDER_ID")
print(f"Using FOLDER_ID: {FOLDER_ID}")

# --- Interfaz Streamlit ---
st.set_page_config(page_title="Google Drive Viewer", page_icon="📁")
st.title("📁 Tus carpetas de Google Drive")

if not FOLDER_ID:
    st.error(f"❌ No se encontró FOLDER_ID en el archivo .env {FOLDER_ID}")
else:
    with st.spinner("Conectando con Google Drive..."):
        folders = list_folders_in_folder(FOLDER_ID)

    if folders:
        st.success(f"Se encontraron {len(folders)} carpetas:")
        for f in folders:
            st.write(f"📂 **{f['name']}** — ID: `{f['id']}`")
    else:
        st.warning("No se encontraron carpetas en el directorio especificado.")
