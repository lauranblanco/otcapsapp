import streamlit as st
import pandas as pd
import sqlite3
from datetime import date

st.set_page_config(page_title="Dashboard Operativo", layout="wide")

conn = sqlite3.connect("database.db")

st.title("🏭 Dashboard Operativo")

# ========================
# KPIs SUPERIORES
# ========================

total_ventas = pd.read_sql_query(
    "SELECT IFNULL(SUM(total),0) as total FROM pedidos",
    conn
)["total"][0]

pedidos_pendientes = pd.read_sql_query(
    "SELECT COUNT(*) as total FROM pedidos WHERE estado='pendiente'",
    conn
)["total"][0]

pedidos_entregados = pd.read_sql_query(
    "SELECT COUNT(*) as total FROM pedidos WHERE estado='entregado'",
    conn
)["total"][0]

gastos_totales = pd.read_sql_query(
    "SELECT IFNULL(SUM(monto),0) as total FROM gastos",
    conn
)["total"][0]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Ventas Totales", f"${total_ventas:,.0f}")
col2.metric("Pedidos Pendientes", pedidos_pendientes)
col3.metric("Pedidos Entregados", pedidos_entregados)
col4.metric("Gastos Totales", f"${gastos_totales:,.0f}")

st.divider()

# ========================
# ESTADO DE PEDIDOS
# ========================

st.subheader("📦 Estado de Pedidos")

estado_df = pd.read_sql_query("""
    SELECT estado, COUNT(*) as cantidad
    FROM pedidos
    GROUP BY estado
""", conn)

col1, col2 = st.columns(2)

with col1:
    st.dataframe(estado_df, use_container_width=True)

with col2:
    st.bar_chart(estado_df.set_index("estado"))

# ========================
# PRÓXIMAS ENTREGAS
# ========================

st.subheader("🚚 Próximas Entregas")

proximos = pd.read_sql_query("""
    SELECT id_pedido, id_cliente, fecha_entrega, total
    FROM pedidos
    WHERE estado='pendiente'
    ORDER BY fecha_entrega ASC
    LIMIT 10
""", conn)

st.dataframe(proximos, use_container_width=True)

# ========================
# VENTAS Y GASTOS
# ========================

st.subheader("📈 Ventas vs Gastos")

ventas_mes = pd.read_sql_query("""
    SELECT strftime('%Y-%m', fecha_entrega) as mes,
           SUM(total) as ventas
    FROM pedidos
    GROUP BY mes
""", conn)

gastos_mes = pd.read_sql_query("""
    SELECT strftime('%Y-%m', fecha) as mes,
           SUM(monto) as gastos
    FROM gastos
    GROUP BY mes
""", conn)

merged = pd.merge(ventas_mes, gastos_mes, on="mes", how="left").fillna(0)

st.line_chart(merged.set_index("mes"), use_container_width=True)
