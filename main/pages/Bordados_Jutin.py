import streamlit as st
from drive_connector import get_drive_service
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from drive_utils import list_folders_in_folder, list_files_in_folder

st.title("🧵 Bordados Jutin")

try:
    service = get_drive_service()
    root_id = st.secrets["ROOT_ID"]

    empresas = list_folders_in_folder(service, root_id)
    if not empresas:
        st.warning("No se encontraron carpetas de empresas.")
    else:
        empresa_seleccionada = st.selectbox("Selecciona una empresa:", [e["name"] for e in empresas])
        carpeta_id = next(e["id"] for e in empresas if e["name"] == empresa_seleccionada)

        st.subheader(f"📊 Estadísticas de {empresa_seleccionada}")
        files = list_files_in_folder(service, carpeta_id)

        if not files:
            st.info("No se encontraron archivos en esta empresa.")
        else:
            st.success(f"Archivos encontrados: {len(files)}")
            for f in files:
                st.write(f"📄 **{f['name']}** — {f['mimeType']} — 📅 {f['modifiedTime']}")
except Exception as e:
    st.error(f"Ocurrió un error: {e}")
