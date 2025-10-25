import streamlit as st
from drive_connector import get_drive_service
from drive_utils import list_folders_in_folder, list_files_in_folder

st.title("🔄 Actualizar información")

try:
    service = get_drive_service()
    root_id = st.secrets["FOLDER"]["ROOT_ID"]

    empresas = list_folders_in_folder(service, root_id)
    if not empresas:
        st.warning("No se encontraron carpetas de empresas.")
    else:
        for empresa in empresas:
            st.subheader(f"🏢 {empresa['name']}")
            if st.button(f"Actualizar {empresa['name']}", key=empresa["id"]):
                files = list_files_in_folder(service, empresa["id"])
                st.success(f"Se actualizaron {len(files)} archivos de {empresa['name']}")
except Exception as e:
    st.error(f"Ocurrió un error: {e}")

