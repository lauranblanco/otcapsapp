import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import date
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
tab1, tab2, tab3, tab4 = st.tabs([
    "📦 Nuevo Pedido",
    "💸 Nuevo Gasto",
    "✏️ Actualizar Datos",
    "⚙️ Administración"
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
        costo = st.number_input("Costo unitario", min_value=0.0, step=1000.0)
        stock = st.number_input("Stock inicial", min_value=0.0, step=1.0)

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
    # TOTAL EDITABLE
    # ======================================================

    total_calculado = sum(item["subtotal"] for item in st.session_state.insumos_pedido)

    if total_calculado > 0:

        total_final = st.number_input(
            "Total del pedido",
            min_value=0.0,
            value=float(total_calculado),
            step=1000.0
        )

        # ======================================================
        # ANTICIPO
        # ======================================================

        anticipo_sugerido = total_final * 0.5

        anticipo = st.number_input(
            "Anticipo",
            min_value=0.0,
            max_value=float(total_final),
            value=float(anticipo_sugerido),
            step=1000.0
        )

        saldo = total_final - anticipo

        st.info(f"Saldo pendiente: ${saldo:,.2f}")

    else:
        total_final = 0
        anticipo = 0
        saldo = 0

    # ======================================================
    # GUARDAR PEDIDO COMPLETO
    # ======================================================

    if st.button("Guardar Pedido Completo"):

        if total_final <= 0:
            st.error("El total debe ser mayor a 0")
            st.stop()

        if anticipo > total_final:
            st.error("El anticipo no puede ser mayor al total")
            st.stop()

        conn = get_connection()
        cursor = conn.cursor()

        # Insertar pedido CON total
        cursor.execute("""
            INSERT INTO pedidos 
            (id_cliente, fecha_anticipo, fecha_entrega, estado, total)
            VALUES (?, ?, ?, ?, ?)
        """, (
            id_cliente,
            fecha_anticipo,
            fecha_entrega,
            estado,
            total_final
        ))

        id_pedido = cursor.lastrowid

        # Insertar detalle
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

        # ==========================
        # CREAR FACTURAS
        # ==========================

        # Factura anticipo
        if anticipo > 0:
            cursor.execute("""
                INSERT INTO facturas
                (id_pedido, tipo, monto, fecha_programada, estado)
                VALUES (?, ?, ?, ?, ?)
            """, (
                id_pedido,
                "anticipo",
                anticipo,
                fecha_anticipo,
                "pendiente"
            ))

        # Factura saldo
        if saldo > 0:
            cursor.execute("""
                INSERT INTO facturas
                (id_pedido, tipo, monto, fecha_programada, estado)
                VALUES (?, ?, ?, ?, ?)
            """, (
                id_pedido,
                "saldo",
                saldo,
                fecha_entrega,
                "pendiente"
            ))

        conn.commit()
        conn.close()

        st.success(f"Pedido guardado correctamente ✅ Total: ${total_final:,.2f}")
        st.session_state.insumos_pedido = []



# ==========================================================
# 💸 TAB 2 - NUEVO GASTO
# ==========================================================
with tab2:

    st.subheader("💸 Registrar Nuevo Gasto")

    with st.form("form_nuevo_gasto"):

        descripcion = st.text_input("Descripción *")
        categoria = st.text_input("Categoría")
        monto = st.number_input("Monto *", min_value=0.0, step=1000.0)
        fecha = st.date_input("Fecha", value=date.today())
        pagado_a = st.text_input("Pagado a")
        medio_pago = st.selectbox(
            "Medio de pago",
            ["Efectivo", "Transferencia", "Tarjeta", "Nequi", "Otro"]
        )

        submitted = st.form_submit_button("Guardar Gasto")

        if submitted:

            if not descripcion:
                st.error("La descripción es obligatoria ❌")
                st.stop()

            if monto <= 0:
                st.error("El monto debe ser mayor a 0 ❌")
                st.stop()

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO gastos 
                (descripcion, categoria, monto, fecha, pagado_a, medio_pago)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                descripcion,
                categoria,
                monto,
                fecha,
                pagado_a,
                medio_pago
            ))

            conn.commit()
            conn.close()

            st.success("Gasto registrado correctamente ✅")
            st.rerun()


# ==========================================================
# ✏️ TAB 3 - ACTUALIZAR DATOS
# ==========================================================

with tab3:

    st.subheader("✏️ Actualizar Datos Existentes")

    tablas = ["clientes", "insumos", "pedidos", "detalle_pedido", "gastos", "facturas"]

    tabla_seleccionada = st.selectbox("Seleccionar tabla", tablas)

    conn = get_connection()
    cursor = conn.cursor()

    # Obtener columnas
    cursor.execute(f"PRAGMA table_info({tabla_seleccionada})")
    columnas_info = cursor.fetchall()

    columnas = [col[1] for col in columnas_info]
    pk_col = columnas[0]  # asumimos primera columna es PK

    # Obtener registros
    cursor.execute(f"SELECT * FROM {tabla_seleccionada}")
    registros = cursor.fetchall()

    if not registros:
        st.warning("No hay registros en esta tabla.")
        conn.close()
        st.stop()

    # Crear diccionario para mostrar opciones
    opciones = {}

    for row in registros:
        row_dict = dict(zip(columnas, row))
        label = f"{row_dict[pk_col]} - " + str(
            row_dict.get("nombre", row_dict.get("descripcion", "Registro"))
        )
        opciones[label] = row_dict

    seleccionado = st.selectbox("Seleccionar registro", list(opciones.keys()))

    registro = opciones[seleccionado]

    st.markdown("### Editar valores")

    nuevos_valores = {}

    for col in columnas:

        if col == pk_col:
            st.text_input(col, value=registro[col], disabled=True)
        else:
            valor_actual = registro[col]

            if isinstance(valor_actual, (int, float)):
                nuevos_valores[col] = st.number_input(
                    col,
                    value=float(valor_actual) if valor_actual is not None else 0.0
                )
            else:
                nuevos_valores[col] = st.text_input(
                    col,
                    value=str(valor_actual) if valor_actual is not None else ""
                )

    if st.button("Guardar cambios"):

        set_clause = ", ".join([f"{col} = ?" for col in nuevos_valores.keys()])
        values = list(nuevos_valores.values())
        values.append(registro[pk_col])

        cursor.execute(
            f"""
            UPDATE {tabla_seleccionada}
            SET {set_clause}
            WHERE {pk_col} = ?
            """,
            values
        )

        conn.commit()
        st.success("Registro actualizado correctamente ✅")
        st.rerun()

    conn.close()


# ==========================================================
# ⚙️ TAB 4 - ADMINISTRACIÓN
# ==========================================================
with tab4:

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

    st.divider()

    st.subheader("📂 Cargar información masiva desde Excel")

    archivo = st.file_uploader(
        "Sube el archivo Excel con las tablas",
        type=["xlsx"]
    )

    if archivo is not None:

        try:
            conn = get_connection()

            # Leer todas las hojas
            excel_data = pd.read_excel(archivo, sheet_name=None)

            tablas_validas = [
                "clientes",
                "insumos",
                "pedidos",
                "detalle_pedido",
                "gastos",
                "facturas"
            ]

            for nombre_hoja, df in excel_data.items():
    
                if nombre_hoja in tablas_validas:
    
                    st.write(f"Procesando tabla: {nombre_hoja}")
    
                    # Eliminar columna ID si existe
                    primary_keys = {
                        "clientes": "id_cliente",
                        "insumos": "id_insumo",
                        "pedidos": "id_pedido",
                        "detalle_pedido": "id_detalle",
                        "gastos": "id_gasto",
                        "facturas": "id_factura"
                    }
                
                    if nombre_hoja in primary_keys:
                        pk = primary_keys[nombre_hoja]
                        if pk in df.columns:
                            df = df.drop(columns=[pk])
                        
                    if nombre_hoja in ["clientes", "insumos"]:
                        # Leer datos existentes
                        df_existente = pd.read_sql(f"SELECT * FROM {nombre_hoja}", conn)
                        # Concatenar existente + nuevo
                        df_combinado = pd.concat([df_existente, df], ignore_index=True)

                        # Eliminar duplicados (ajusta subset según tus columnas únicas)
                        if nombre_hoja == "clientes":
                            # Ejemplo: asumiendo que email es único
                            df_sin_duplicados = df_combinado.drop_duplicates(subset=['nombre', 'email', 'telefono'], keep='last')
                        elif nombre_hoja == "insumos":
                            # Ejemplo: asumiendo que código es único
                            df_sin_duplicados = df_combinado.drop_duplicates(subset=['nombre'], keep='last')
                                
                        # Reemplazar toda la tabla
                        df_sin_duplicados.to_sql(
                            nombre_hoja,
                            conn,
                            if_exists="replace",
                            index=False
                        )
                    else:
                        # Para otras tablas, solo append normal
                        df.to_sql(
                            nombre_hoja,
                            conn,
                            if_exists="append",
                            index=False
                        )

                    conn.commit()
            conn.close()

            st.success("✅ Información cargada correctamente.")

        except Exception as e:
            st.error(f"❌ Error al cargar datos: {e}")


