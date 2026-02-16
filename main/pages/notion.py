import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Dashboard", layout="wide")

conn = sqlite3.connect("database.db")

st.title("📊 Resumen General")

# --- KPIs ---
total_ventas = pd.read_sql_query(
    "SELECT IFNULL(SUM(total),0) as total FROM pedidos WHERE estado != 'cancelado'",
    conn
)["total"][0]

gastos_mes = pd.read_sql_query("""
    SELECT IFNULL(SUM(monto),0) as total
    FROM gastos
    WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m','now')
""", conn)["total"][0]

pedidos_activos = pd.read_sql_query(
    "SELECT COUNT(*) as total FROM pedidos WHERE estado='pendiente'",
    conn
)["total"][0]

clientes = pd.read_sql_query(
    "SELECT COUNT(*) as total FROM clientes",
    conn
)["total"][0]

utilidad = total_ventas - gastos_mes

# --- Fila principal ---
col1, col2, col3, col4 = st.columns(4)

col1.metric("Ventas Totales", f"${total_ventas:,.0f}")
col2.metric("Utilidad Estimada", f"${utilidad:,.0f}")
col3.metric("Pedidos Activos", pedidos_activos)
col4.metric("Clientes", clientes)

st.divider()

# --- Ventas por mes ---
st.subheader("Tendencia de Ventas")

ventas_mes = pd.read_sql_query("""
    SELECT strftime('%Y-%m', fecha_entrega) as mes,
           SUM(total) as total
    FROM pedidos
    WHERE estado != 'cancelado'
    GROUP BY mes
    ORDER BY mes
""", conn)

st.line_chart(ventas_mes.set_index("mes"), use_container_width=True)

# --- Alertas suaves ---
if utilidad < 0:
    st.warning("⚠️ La utilidad del mes es negativa.")
