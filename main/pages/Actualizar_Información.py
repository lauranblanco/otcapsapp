import streamlit as st
import os
from db_init import init_db
from db import DB_PATH

st.title("🔄 Actualizar Información")

# Crear pestañas
tab1, tab2, tab3 = st.tabs([
    "📦 Nuevo Pedido",
    "💸 Nuevo Gasto",
    "⚙️ Administración de Datos"
])

# ==========================================================
# 📦 TAB 1 - NUEVO PEDIDO
# ==========================================================
with tab1:

    st.subheader("Registrar Nuevo Pedido")

    with st.form("form_nuevo_pedido"):
        cliente = st.text_input("Nombre del cliente")
        producto = st.text_input("Producto")
        cantidad = st.number_input("Cantidad", min_value=1, step=1)
        precio = st.number_input("Precio unitario", min_value=0.0, step=0.5)

        submitted = st.form_submit_button("Guardar Pedido")

        if submitted:
            # Aquí luego llamaremos tu función para insertar en DB
            st.success("Pedido guardado correctamente ✅")


# ==========================================================
# 💸 TAB 2 - NUEVO GASTO
# ==========================================================
with tab2:

    st.subheader("Registrar Nuevo Gasto")

    with st.form("form_nuevo_gasto"):
        descripcion = st.text_input("Descripción del gasto")
        categoria = st.text_input("Categoría")
        monto = st.number_input("Monto", min_value=0.0, step=0.5)
        fecha = st.date_input("Fecha")

        submitted = st.form_submit_button("Guardar Gasto")

        if submitted:
            # Aquí luego insertaremos en DB
            st.success("Gasto guardado correctamente ✅")


# ==========================================================
# ⚙️ TAB 3 - ADMINISTRACIÓN
# ==========================================================
with tab3:

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


