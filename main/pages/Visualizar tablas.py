import streamlit as st
import pandas as pd
import sqlite3
import io
from datetime import datetime
from db import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)

def load_data(query, params=None):
    conn = get_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def exportar_toda_la_base():
    conn = get_connection()
    
    # Cargar todas las tablas
    df_clientes = pd.read_sql_query("SELECT * FROM clientes", conn)
    df_insumos = pd.read_sql_query("SELECT * FROM insumos", conn)
    df_pedidos = pd.read_sql_query("SELECT * FROM pedidos", conn)
    df_detalle = pd.read_sql_query("SELECT * FROM detalle_pedido", conn)
    df_gastos = pd.read_sql_query("SELECT * FROM gastos", conn)

    conn.close()

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_clientes.to_excel(writer, sheet_name="Clientes", index=False)
        df_insumos.to_excel(writer, sheet_name="Insumos", index=False)
        df_pedidos.to_excel(writer, sheet_name="Pedidos", index=False)
        df_detalle.to_excel(writer, sheet_name="Detalle_Pedido", index=False)
        df_gastos.to_excel(writer, sheet_name="Gastos", index=False)

    output.seek(0)

    fecha = datetime.today().strftime("%Y%m%d")

    st.download_button(
        label="📥 Descargar Base Completa",
        data=output,
        file_name=f"respaldo_base_{fecha}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.title("📊 Visualizar Tablas")

st.markdown("### Respaldo General")

exportar_toda_la_base()

st.divider()


tab1, tab2, tab3, tab4 = st.tabs(
    ["Clientes", "Insumos", "Pedidos", "Gastos"]
)

with tab1:
    st.subheader("Clientes")

    conn = get_connection()

    df_nombres = pd.read_sql_query(
        "SELECT DISTINCT nombre FROM clientes ORDER BY nombre",
        conn
    )
    conn.close()

    lista_clientes = df_nombres["nombre"].tolist()

    filtro_clientes = st.multiselect(
        "Seleccionar cliente(s)",
        lista_clientes
    )

    query = "SELECT * FROM clientes"
    condiciones = []
    params = []

    if filtro_clientes:
        placeholders = ",".join(["?"] * len(filtro_clientes))
        condiciones.append(f"nombre IN ({placeholders})")
        params.extend(filtro_clientes)

    if condiciones:
        query += " WHERE " + " AND ".join(condiciones)

    df_clientes = load_data(query, params)

    st.metric("Total Clientes", len(df_clientes))
    st.dataframe(df_clientes, use_container_width=True)

with tab2:
    st.subheader("Insumos")

    conn = get_connection()

    df_nombres = pd.read_sql_query(
        "SELECT DISTINCT nombre FROM insumos ORDER BY nombre",
        conn
    )

    df_unidades = pd.read_sql_query(
        "SELECT DISTINCT unidad_medida FROM insumos ORDER BY unidad_medida",
        conn
    )

    conn.close()

    filtro_nombre = st.multiselect(
        "Seleccionar insumo(s)",
        df_nombres["nombre"].dropna().tolist()
    )

    filtro_unidad = st.multiselect(
        "Unidad de medida",
        df_unidades["unidad_medida"].dropna().tolist()
    )

    query = "SELECT * FROM insumos"
    condiciones = []
    params = []

    if filtro_nombre:
        placeholders = ",".join(["?"] * len(filtro_nombre))
        condiciones.append(f"nombre IN ({placeholders})")
        params.extend(filtro_nombre)

    if filtro_unidad:
        placeholders = ",".join(["?"] * len(filtro_unidad))
        condiciones.append(f"unidad_medida IN ({placeholders})")
        params.extend(filtro_unidad)

    if condiciones:
        query += " WHERE " + " AND ".join(condiciones)

    df_insumos = load_data(query, params)

    st.metric("Total Insumos", len(df_insumos))
    st.dataframe(df_insumos, use_container_width=True)


with tab3:
    st.subheader("Pedidos")

    subtab1, subtab2 = st.tabs(["📦 Resumen Pedidos", "📋 Detalle Pedido"])

    with subtab1:

        conn = get_connection()

        df_clientes = pd.read_sql_query(
            "SELECT id_cliente, nombre FROM clientes ORDER BY nombre",
            conn
        )

        df_estados = pd.read_sql_query(
            "SELECT DISTINCT estado FROM pedidos",
            conn
        )

        conn.close()

        cliente_dict = dict(zip(df_clientes["nombre"], df_clientes["id_cliente"]))

        filtro_cliente = st.multiselect(
            "Cliente(s)",
            list(cliente_dict.keys())
        )

        filtro_estado = st.multiselect(
            "Estado",
            df_estados["estado"].dropna().tolist()
        )

        fecha_inicio = st.date_input("Desde", key="ped_desde")
        fecha_fin = st.date_input("Hasta", key="ped_hasta")

        query = "SELECT * FROM pedidos"
        condiciones = []
        params = []

        if filtro_cliente:
            ids = [cliente_dict[n] for n in filtro_cliente]
            placeholders = ",".join(["?"] * len(ids))
            condiciones.append(f"id_cliente IN ({placeholders})")
            params.extend(ids)

        if filtro_estado:
            placeholders = ",".join(["?"] * len(filtro_estado))
            condiciones.append(f"estado IN ({placeholders})")
            params.extend(filtro_estado)

        if fecha_inicio:
            condiciones.append("fecha_entrega >= ?")
            params.append(fecha_inicio)

        if fecha_fin:
            condiciones.append("fecha_entrega <= ?")
            params.append(fecha_fin)

        if condiciones:
            query += " WHERE " + " AND ".join(condiciones)

        query += " ORDER BY id_pedido DESC"

        df_pedidos = load_data(query, params)

        total_pedidos = len(df_pedidos)
        total_ventas = df_pedidos["total"].sum() if not df_pedidos.empty else 0

        col1, col2 = st.columns(2)
        col1.metric("Total Pedidos", total_pedidos)
        col2.metric("Total Ventas", f"${total_ventas:,.0f}")

        st.dataframe(df_pedidos, use_container_width=True)

    with subtab2:

        conn = get_connection()

        df_pedidos_ids = pd.read_sql_query(
            "SELECT id_pedido FROM pedidos ORDER BY id_pedido DESC",
            conn
        )

        df_insumos = pd.read_sql_query(
            "SELECT id_insumo, nombre FROM insumos ORDER BY nombre",
            conn
        )

        conn.close()

        filtro_pedido = st.multiselect(
            "ID Pedido",
            df_pedidos_ids["id_pedido"].tolist()
        )

        insumo_dict = dict(zip(df_insumos["nombre"], df_insumos["id_insumo"]))

        filtro_insumo = st.multiselect(
            "Insumo(s)",
            list(insumo_dict.keys())
        )

        query = "SELECT * FROM detalle_pedido"
        condiciones = []
        params = []

        if filtro_pedido:
            placeholders = ",".join(["?"] * len(filtro_pedido))
            condiciones.append(f"id_pedido IN ({placeholders})")
            params.extend(filtro_pedido)

        if filtro_insumo:
            ids = [insumo_dict[n] for n in filtro_insumo]
            placeholders = ",".join(["?"] * len(ids))
            condiciones.append(f"id_insumo IN ({placeholders})")
            params.extend(ids)

        if condiciones:
            query += " WHERE " + " AND ".join(condiciones)

        query += " ORDER BY id_detalle DESC"

        df_detalle = load_data(query, params)

        total_lineas = len(df_detalle)
        total_detalle = df_detalle["subtotal"].sum() if not df_detalle.empty else 0

        col1, col2 = st.columns(2)
        col1.metric("Total Líneas", total_lineas)
        col2.metric("Total Subtotal", f"${total_detalle:,.0f}")

        st.dataframe(df_detalle, use_container_width=True)




with tab4:
    st.subheader("Gastos")

    conn = get_connection()

    df_categoria = pd.read_sql_query(
        "SELECT DISTINCT categoria FROM gastos ORDER BY categoria",
        conn
    )

    df_medio = pd.read_sql_query(
        "SELECT DISTINCT medio_pago FROM gastos ORDER BY medio_pago",
        conn
    )

    conn.close()

    filtro_categoria = st.multiselect(
        "Categoría",
        df_categoria["categoria"].dropna().tolist()
    )

    filtro_medio = st.multiselect(
        "Medio de pago",
        df_medio["medio_pago"].dropna().tolist()
    )

    fecha_inicio = st.date_input("Desde", key="gasto_desde")
    fecha_fin = st.date_input("Hasta", key="gasto_hasta")

    query = "SELECT * FROM gastos"
    condiciones = []
    params = []

    if filtro_categoria:
        placeholders = ",".join(["?"] * len(filtro_categoria))
        condiciones.append(f"categoria IN ({placeholders})")
        params.extend(filtro_categoria)

    if filtro_medio:
        placeholders = ",".join(["?"] * len(filtro_medio))
        condiciones.append(f"medio_pago IN ({placeholders})")
        params.extend(filtro_medio)

    if fecha_inicio:
        condiciones.append("fecha >= ?")
        params.append(fecha_inicio)

    if fecha_fin:
        condiciones.append("fecha <= ?")
        params.append(fecha_fin)

    if condiciones:
        query += " WHERE " + " AND ".join(condiciones)

    df_gastos = load_data(query, params)

    total_gastos = df_gastos["monto"].sum() if not df_gastos.empty else 0

    st.metric("Total Gastos", f"${total_gastos:,.0f}")
    st.dataframe(df_gastos, use_container_width=True)
