import streamlit as st
from modules.drive_utils import list_files_in_folder, load_csv_from_drive

FOLDER_ID = "Seguimiento empresas"

st.title("📊 Dashboard de Datos desde Google Drive")

files = list_files_in_folder(FOLDER_ID)

if files:
    selected_file = st.selectbox("Selecciona un archivo:", [f["name"] for f in files])
    file_id = next(f["id"] for f in files if f["name"] == selected_file)
    
    st.write("Cargando datos...")
    df = load_csv_from_drive(file_id)
    st.dataframe(df)
else:
    st.warning("No se encontraron archivos en la carpeta de Drive.")
