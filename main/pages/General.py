import streamlit as st
from drive_connector import get_drive_service
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from drive_utils import list_folders_in_folder, list_files_in_folder


st.title("🌍 Estadísticas Generales")

try:
    service = get_drive_service()
    root_id = st.secrets["ROOT_ID"]
    empresas = list_folders_in_folder(service, root_id)

    if not empresas:
        st.warning("No se encontraron subcarpetas (empresas) en la carpeta raíz de Drive.")
    else:
        st.success(f"Se detectaron {len(empresas)} empresas:")
        for e in empresas:
            st.write(f"🏢 **{e['name']}** — 📁 ID: `{e['id']}`")

except Exception as e:
    st.error(f"Ocurrió un error: {e}")