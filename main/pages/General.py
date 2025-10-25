import streamlit as st
from drive_connector import get_drive_service
from main.drive_utils import list_folders_in_folder

st.title("🌍 Estadísticas Generales")

try:
    service = get_drive_service()
    root_id = st.secrets["FOLDER"]["ROOT_ID"]
    empresas = list_folders_in_folder(service, root_id)

    if not empresas:
        st.warning("No se encontraron subcarpetas (empresas) en la carpeta raíz de Drive.")
    else:
        st.success(f"Se detectaron {len(empresas)} empresas:")
        for e in empresas:
            st.write(f"🏢 **{e['name']}** — 📁 ID: `{e['id']}`")

except Exception as e:
    st.error(f"Ocurrió un error: {e}")