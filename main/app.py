import streamlit as st
from modules.drive_connector import connect_to_drive
from modules.drive_utils import list_folders_in_folder
import os

# Conectar con Google Drive
service = connect_to_drive()

# Obtener el folder_id del .env
FOLDER_ID = os.getenv("FOLDER_ID")

st.title("Carpetas en Google Drive")

if service and FOLDER_ID:
    folders = list_folders_in_folder(service, FOLDER_ID)
    if folders:
        st.subheader("Carpetas encontradas:")
        for folder in folders:
            st.write(f"📁 {folder['name']}  —  ID: {folder['id']}")
    else:
        st.warning("No se encontraron carpetas dentro del folder indicado.")
else:
    st.error("Error al conectar con Google Drive o falta FOLDER_ID en el archivo .env.")

