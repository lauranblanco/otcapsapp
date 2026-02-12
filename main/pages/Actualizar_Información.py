import streamlit as st
import os
from db_init import init_db
from db import DB_PATH

st.title("🔄 Actualizar Información")

st.divider()
st.subheader("⚠️ Zona Administrativa")

# Estado interno
if "confirm_reset" not in st.session_state:
    st.session_state.confirm_reset = False

if "reset_attempts" not in st.session_state:
    st.session_state.reset_attempts = 0


# Botón inicial
if st.button("🗑 Reiniciar Base de Datos"):
    st.session_state.confirm_reset = True


# Flujo de confirmación
if st.session_state.confirm_reset:

    password = st.text_input(
        "Ingrese la clave administrativa para confirmar:",
        type="password"
    )

    if st.button("Confirmar reinicio"):
        if password == st.secrets["RESET_DB_PASSWORD"]:

            if os.path.exists(DB_PATH):
                os.remove(DB_PATH)

            init_db()

            st.success("Base de datos reiniciada correctamente ✅")
            st.session_state.confirm_reset = False
            st.session_state.reset_attempts = 0

        else:
            st.session_state.reset_attempts += 1
            st.error("Clave incorrecta ❌")

            if st.session_state.reset_attempts >= 3:
                st.warning("Demasiados intentos fallidos. Recargue la página.")


