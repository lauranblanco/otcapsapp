import sys
import os

# --- Configurar rutas para importar correctamente ---
current_dir = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.join(current_dir, "modules")
if modules_path not in sys.path:
    sys.path.append(modules_path)

# --- Importaciones ---
import streamlit as st
from dotenv import load_dotenv
from drive_utils import list_folders_in_folder

# --- Cargar variables de entorno ---
load_dotenv(os.path.join(current_dir, ".env"))

# --- Obtener ID de carpeta de Google Drive ---
FOLDER_ID = os.getenv("FOLDER_ID")

st.set_page_config(page_title="Google Drive App", page_icon="📁")
st.title("📁 Explorador de Google Drive")

if not FOLDER_ID:
    st.error("❌ No se encontró FOLDER_ID en el archivo .env")
else:
    try:
        st.write("📂 **Carpeta raíz:**", FOLDER_ID)
        folders = list_folders_in_folder(FOLDER_ID)
        if not folders:
            st.info("No se encontraron subcarpetas en esta carpeta.")
        else:
            for folder in folders:
                st.write(f"📁 {folder['name']} — ID: {folder['id']}")
    except Exception as e:
        st.error(f"⚠️ Error al conectar con Google Drive: {e}")
