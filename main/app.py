import streamlit as st
import pandas as pd
import sqlite3
from db import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)

st.set_page_config(page_title="Resumen Operativo", layout="wide")

conn = get_connection()

st.title("🏭 Resumen Operativo")

# ==================================================
# 🔴 1. SITUACIÓN CRÍTICA (LO MÁS IMPORTANTE)
# ==================================================

pedidos_df = pd.read_sql_query("SELECT * FROM pedidos", conn)

pedidos_pendientes = pedidos_df[pedidos_df["estado"]=="pendiente"]
pedidos_entregados = pedidos_df[pedidos_df["estado"]=="entregado"]

atrasados = pd.read_sql_query("""
    SELECT id_pedido, id_cliente, fecha_entrega, total
    FROM pedidos
    WHERE estado='pendiente'
    AND fecha_entrega < date('now')
    ORDER BY fecha_entrega ASC
""", conn)

# Tiempo promedio entrega
tiempos = pd.read_sql_query("""
    SELECT julianday(fecha_entrega) - julianday(fecha_anticipo) as dias
    FROM pedidos
    WHERE estado='entregado'
""", conn)

promedio_dias = tiempos["dias"].mean() if not tiempos.empty else 0

# Cumplimiento %
total_entregados = len(pedidos_entregados)
entregados_a_tiempo = pd.read_sql_query("""
    SELECT COUNT(*) as total
    FROM pedidos
    WHERE estado='entregado'
    AND fecha_entrega >= fecha_anticipo
""", conn)["total"][0]

cumplimiento = (
    (entregados_a_tiempo / total_entregados) * 100
    if total_entregados > 0 else 0
)

st.subheader("🔴 Situación Actual")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Pedidos Pendientes", len(pedidos_pendientes))
col2.metric("Pedidos Atrasados", len(atrasados))
col3.metric("Promedio Días Entrega", f"{promedio_dias:.1f}")
col4.metric("Cumplimiento Entrega", f"{cumplimiento:.1f}%")

if len(atrasados) > 0:
    st.error("Hay pedidos fuera de tiempo.")
    
st.divider()

# ==================================================
# 📊 2. ESTADO GENERAL
# ==================================================

total_ventas = pedidos_df["total"].sum()
gastos_totales = pd.read_sql_query(
    "SELECT IFNULL(SUM(monto),0) as total FROM gastos",
    conn
)["total"][0]

st.subheader("📊 Estado General")

col1, col2, col3 = st.columns(3)

col1.metric("Ventas Totales", f"${total_ventas:,.0f}")
col2.metric("Pedidos Entregados", len(pedidos_entregados))
col3.metric("Gastos Totales", f"${gastos_totales:,.0f}")

estado_df = pd.read_sql_query("""
    SELECT estado, COUNT(*) as cantidad
    FROM pedidos
    GROUP BY estado
""", conn)

st.bar_chart(estado_df.set_index("estado"))

st.divider()

# ==================================================
# 🚚 3. PRÓXIMAS ENTREGAS
# ==================================================

st.subheader("🚚 Próximas Entregas")

proximos = pd.read_sql_query("""
    SELECT id_pedido, id_cliente, fecha_entrega, total
    FROM pedidos
    WHERE estado='pendiente'
    ORDER BY fecha_entrega ASC
    LIMIT 10
""", conn)

st.dataframe(proximos, use_container_width=True)

st.divider()

# ==================================================
# 📈 4. CARGA OPERATIVA Y TENDENCIA
# ==================================================

st.subheader("📈 Carga Operativa por Semana")

carga = pd.read_sql_query("""
    SELECT strftime('%Y-%W', fecha_entrega) as semana,
           COUNT(*) as pedidos
    FROM pedidos
    GROUP BY semana
    ORDER BY semana
""", conn)

st.bar_chart(carga.set_index("semana"))

st.subheader("💰 Ventas vs Gastos")

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

st.line_chart(merged.set_index("mes"))

st.divider()

# ==================================================
# 👥 5. CLIENTES MÁS ACTIVOS
# ==================================================

st.subheader("👥 Clientes Más Activos (Mes Actual)")

clientes_mes = pd.read_sql_query("""
    SELECT id_cliente, COUNT(*) as pedidos
    FROM pedidos
    WHERE strftime('%Y-%m', fecha_entrega)=strftime('%Y-%m','now')
    GROUP BY id_cliente
    ORDER BY pedidos DESC
    LIMIT 5
""", conn)

st.dataframe(clientes_mes, use_container_width=True)

st.divider()

# ==================================================
# 📦 6. INSUMOS MÁS UTILIZADOS
# ==================================================

st.subheader("📦 Insumos Más Utilizados")

insumos = pd.read_sql_query("""
    SELECT id_insumo, SUM(cantidad) as total_usado
    FROM detalle_pedido
    GROUP BY id_insumo
    ORDER BY total_usado DESC
    LIMIT 5
""", conn)

st.dataframe(insumos, use_container_width=True)
