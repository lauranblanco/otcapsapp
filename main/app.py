import streamlit as st
from modules.drive_utils import list_files_in_folder, load_csv_from_drive
from dotenv import load_dotenv
import os

# Cargar variables del .env
load_dotenv("main/.env")

FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

st.title("📊 Dashboard de Datos desde Google Drive")

# Mostrar archivos en la carpeta
files = list_files_in_folder(FOLDER_ID)

if files:
    selected_file = st.selectbox("Selecciona un archivo:", [f["name"] for f in files])
    file_id = next(f["id"] for f in files if f["name"] == selected_file)

    st.write("Cargando datos desde Google Drive...")
    df = load_csv_from_drive(file_id)

    if df is not None:
        st.dataframe(df)
    else:
        st.error("❌ No se pudo cargar el archivo. Verifica que sea un CSV válido.")
else:
    st.warning("⚠️ No se encontraron archivos en la carpeta de Drive.")
