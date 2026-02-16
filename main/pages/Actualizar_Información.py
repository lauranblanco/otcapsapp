import streamlit as st
import sqlite3
import os
from db_init import init_db
from db import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_clientes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_cliente, nombre FROM clientes")
    data = cursor.fetchall()
    conn.close()
    return data

def get_insumos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_insumo, nombre, costo_unitario FROM insumos")
    data = cursor.fetchall()
    conn.close()
    return data

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

    clientes = get_clientes()
    clientes_dict = {nombre: id_cliente for id_cliente, nombre in clientes}
    opciones_clientes = list(clientes_dict.keys()) + ["➕ Nuevo cliente"]

    cliente_seleccionado = st.selectbox("Cliente", opciones_clientes)

    # ======================================================
    # NUEVO CLIENTE
    # ======================================================
    if cliente_seleccionado == "➕ Nuevo cliente":

        st.markdown("### Datos del nuevo cliente")

        nombre = st.text_input("Nombre")
        telefono = st.text_input("Teléfono")
        email = st.text_input("Email")
        direccion = st.text_input("Dirección")

        if st.button("Guardar Cliente"):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clientes (nombre, telefono, email, direccion)
                VALUES (?, ?, ?, ?)
            """, (nombre, telefono, email, direccion))
            conn.commit()
            conn.close()
            st.success("Cliente creado correctamente ✅")
            st.rerun()

        st.stop()

    else:
        id_cliente = clientes_dict[cliente_seleccionado]

    # ======================================================
    # DATOS DEL PEDIDO
    # ======================================================

    fecha_entrega = st.date_input("Fecha de entrega")
    fecha_anticipo = st.date_input("Fecha de anticipo")
    estado = st.selectbox("Estado", ["pendiente", "en_proceso", "entregado"])

    # ======================================================
    # INSUMOS
    # ======================================================

    st.markdown("### Insumos del pedido")

    if "insumos_pedido" not in st.session_state:
        st.session_state.insumos_pedido = []

    insumos = get_insumos()
    insumos_dict = {nombre: (id_insumo, costo) for id_insumo, nombre, costo in insumos}
    opciones_insumos = list(insumos_dict.keys()) + ["➕ Nuevo insumo"]

    insumo_sel = st.selectbox("Insumo", opciones_insumos)
    cantidad = st.number_input("Cantidad", min_value=0.0, step=1.0)

    # NUEVO INSUMO
    if insumo_sel == "➕ Nuevo insumo":

        st.markdown("### Crear nuevo insumo")

        nombre_insumo = st.text_input("Nombre del insumo")
        unidad = st.text_input("Unidad de medida")
        costo = st.number_input("Costo unitario", min_value=0.0)
        stock = st.number_input("Stock inicial", min_value=0.0)

        if st.button("Guardar Insumo"):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO insumos (nombre, unidad_medida, costo_unitario, stock_actual)
                VALUES (?, ?, ?, ?)
            """, (nombre_insumo, unidad, costo, stock))
            conn.commit()
            conn.close()
            st.success("Insumo creado correctamente ✅")
            st.rerun()

        st.stop()

    else:
        if st.button("Agregar insumo al pedido"):
            id_insumo, costo_unitario = insumos_dict[insumo_sel]
            subtotal = cantidad * costo_unitario

            st.session_state.insumos_pedido.append({
                "id_insumo": id_insumo,
                "nombre": insumo_sel,
                "cantidad": cantidad,
                "precio_unitario": costo_unitario,
                "subtotal": subtotal
            })

    # Mostrar tabla temporal
    if st.session_state.insumos_pedido:
        st.table(st.session_state.insumos_pedido)

    # ======================================================
    # GUARDAR PEDIDO COMPLETO
    # ======================================================

    if st.button("Guardar Pedido Completo"):

        conn = get_connection()
        cursor = conn.cursor()

        # Insertar pedido
        cursor.execute("""
            INSERT INTO pedidos (id_cliente, fecha_anticipo, fecha_entrega, estado)
            VALUES (?, ?, ?, ?)
        """, (id_cliente, fecha_anticipo, fecha_entrega, estado))

        id_pedido = cursor.lastrowid

        total = 0

        for item in st.session_state.insumos_pedido:
            cursor.execute("""
                INSERT INTO detalle_pedido
                (id_pedido, id_insumo, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (
                id_pedido,
                item["id_insumo"],
                item["cantidad"],
                item["precio_unitario"],
                item["subtotal"]
            ))

            total += item["subtotal"]

        # Actualizar total del pedido
        cursor.execute("""
            UPDATE pedidos
            SET total = ?
            WHERE id_pedido = ?
        """, (total, id_pedido))

        conn.commit()
        conn.close()

        st.success(f"Pedido guardado correctamente ✅ Total: ${total:.2f}")
        st.session_state.insumos_pedido = []


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


