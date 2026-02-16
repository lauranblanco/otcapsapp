import streamlit as st
import pandas as pd
import sqlite3
from db import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)

def load_data(query, params=None):
    conn = get_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

st.title("📊 Visualizar Tablas")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Clientes", "Insumos", "Pedidos", "Gastos"]
)

with tab1:
    st.subheader("Clientes")

    filtro_nombre = st.text_input("Filtrar por nombre")

    query = "SELECT * FROM clientes"
    params = []

    if filtro_nombre:
        query += " WHERE nombre LIKE ?"
        params.append(f"%{filtro_nombre}%")

    df_clientes = load_data(query, params)

    st.metric("Total Clientes", len(df_clientes))
    st.dataframe(df_clientes, use_container_width=True)


with tab2:
    st.subheader("Insumos")

    filtro_nombre = st.text_input("Filtrar por nombre", key="insumo_nombre")
    filtro_unidad = st.text_input("Filtrar por unidad de medida", key="insumo_unidad")

    query = "SELECT * FROM insumos"
    condiciones = []
    params = []

    if filtro_nombre:
        condiciones.append("nombre LIKE ?")
        params.append(f"%{filtro_nombre}%")

    if filtro_unidad:
        condiciones.append("unidad_medida LIKE ?")
        params.append(f"%{filtro_unidad}%")

    if condiciones:
        query += " WHERE " + " AND ".join(condiciones)

    df_insumos = load_data(query, params)

    st.metric("Total Insumos", len(df_insumos))
    st.dataframe(df_insumos, use_container_width=True)


with tab3:
    st.subheader("Pedidos")

    filtro_cliente = st.text_input("Filtrar por cliente")
    filtro_estado = st.selectbox(
        "Filtrar por estado",
        ["Todos", "pendiente", "entregado", "cancelado"]
    )

    query = """
        SELECT 
            p.id_pedido,
            c.nombre AS cliente,
            p.fecha_anticipo,
            p.fecha_entrega,
            p.estado,
            p.total
        FROM pedidos p
        JOIN clientes c ON p.id_cliente = c.id_cliente
    """

    condiciones = []
    params = []

    if filtro_cliente:
        condiciones.append("c.nombre LIKE ?")
        params.append(f"%{filtro_cliente}%")

    if filtro_estado != "Todos":
        condiciones.append("p.estado = ?")
        params.append(filtro_estado)

    if condiciones:
        query += " WHERE " + " AND ".join(condiciones)

    df_pedidos = load_data(query, params)

    st.metric("Total Pedidos", len(df_pedidos))
    st.dataframe(df_pedidos, use_container_width=True)

    st.divider()
    st.subheader("Ver detalle de pedido")

    id_pedido = st.number_input("Ingrese ID del pedido", min_value=1, step=1)

    if st.button("Ver detalle"):
        query_detalle = """
            SELECT 
                d.id_detalle,
                i.nombre AS insumo,
                d.cantidad,
                d.precio_unitario,
                d.subtotal
            FROM detalle_pedido d
            JOIN insumos i ON d.id_insumo = i.id_insumo
            WHERE d.id_pedido = ?
        """

        df_detalle = load_data(query_detalle, [id_pedido])

        if df_detalle.empty:
            st.warning("No se encontró detalle para este pedido")
        else:
            st.dataframe(df_detalle, use_container_width=True)


with tab4:
    st.subheader("Gastos")

    filtro_categoria = st.text_input("Filtrar por categoría")
    fecha_inicio = st.date_input("Desde", key="fecha_inicio")
    fecha_fin = st.date_input("Hasta", key="fecha_fin")

    query = "SELECT * FROM gastos WHERE 1=1"
    params = []

    if filtro_categoria:
        query += " AND categoria LIKE ?"
        params.append(f"%{filtro_categoria}%")

    if fecha_inicio:
        query += " AND fecha >= ?"
        params.append(fecha_inicio)

    if fecha_fin:
        query += " AND fecha <= ?"
        params.append(fecha_fin)

    df_gastos = load_data(query, params)

    st.metric("Total Gastos", f"${df_gastos['monto'].sum():,.0f}" if not df_gastos.empty else "$0")
    st.dataframe(df_gastos, use_container_width=True)



