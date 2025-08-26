import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Mi Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Menú principal en sidebar
with st.sidebar:
    st.title("📊 Mi Dashboard")
    page = st.radio(
        "Navegación",
        ["Dashboard"],
        index=0
    )

# Navegación entre páginas
if page == "Dashboard":
    from pages import gorras
    gorras.show()