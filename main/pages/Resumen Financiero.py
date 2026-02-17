import streamlit as st
import pandas as pd
import sqlite3
from db import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)

st.set_page_config(page_title="Dashboard Financiero", layout="wide")

st.title("🏦 Resumen Financiero")

# =========================
# CONEXIÓN
# =========================

conn = get_connection()

# =========================
# CARGA DE DATOS BASE
# =========================

pedidos_df = pd.read_sql_query("""
    SELECT * FROM pedidos
    WHERE estado != 'cancelado'
""", conn)

gastos_df = pd.read_sql_query("SELECT * FROM gastos", conn)

clientes_df = pd.read_sql_query("SELECT * FROM clientes", conn)

# Si no hay datos evitar errores
if pedidos_df.empty:
    st.warning("No hay datos de pedidos registrados.")
    st.stop()

# =========================
# MÉTRICAS BASE
# =========================

ventas_totales = pedidos_df["total"].sum()
gastos_totales = gastos_df["monto"].sum()
ebitda = ventas_totales - gastos_totales

ticket_promedio = pedidos_df["total"].mean()

margen_operativo = (ebitda / ventas_totales * 100) if ventas_totales > 0 else 0

utilidad = ebitda

# =========================
# KPIs ESTRATÉGICOS
# =========================

st.subheader("📊 Indicadores Estratégicos")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Clientes", f"{clientes_df.shape[0]}")
col2.metric("Ventas Totales", f"${ventas_totales:,.0f}")
col3.metric("Utilidad Operativa", f"{utilidad:.1f}")
#col2.metric("EBITDA", f"${ebitda:,.0f}")
#col3.metric("Margen Operativo", f"{margen_operativo:.1f}%")
col4.metric("Factura Promedio", f"${ticket_promedio:,.0f}")

st.divider()

# =========================
# RENTABILIDAD MENSUAL
# =========================

st.subheader("📈 Rentabilidad Mensual")

pedidos_df["mes"] = pd.to_datetime(pedidos_df["fecha_entrega"]).dt.to_period("M")
gastos_df["mes"] = pd.to_datetime(gastos_df["fecha"]).dt.to_period("M")

ventas_mes = pedidos_df.groupby("mes")["total"].sum().reset_index()
gastos_mes = gastos_df.groupby("mes")["monto"].sum().reset_index()

finanzas = pd.merge(ventas_mes, gastos_mes, on="mes", how="left").fillna(0)
finanzas["utilidad"] = finanzas["total"] - finanzas["monto"]
finanzas["margen"] = (finanzas["utilidad"] / finanzas["total"]) * 100

st.line_chart(finanzas.set_index("mes")[["total","utilidad"]])

st.divider()

# =========================
# VOLATILIDAD
# =========================

volatilidad = finanzas["total"].std()
# st.metric("Volatilidad de Ventas", f"${volatilidad:,.0f}")

# st.divider()

# =========================
# CONCENTRACIÓN DE CLIENTES
# =========================

st.subheader("🏆 Concentración de Ingresos")

cliente_ingresos = pedidos_df.groupby("id_cliente")["total"].sum().reset_index()
cliente_ingresos = cliente_ingresos.sort_values("total", ascending=False)

top_3 = cliente_ingresos.head(3)["total"].sum()
concentracion = (top_3 / ventas_totales) * 100 if ventas_totales > 0 else 0

col1, col2 = st.columns(2)

col1.metric("Dependencia Top 3 Clientes", f"{concentracion:.1f}%")

col2.dataframe(cliente_ingresos.head(5), use_container_width=True)

st.divider()

# =========================
# RENTABILIDAD POR CLIENTE
# =========================

st.subheader("💎 Rentabilidad por Cliente")

rentabilidad_cliente = pedidos_df.groupby("id_cliente").agg(
    ingresos=("total","sum"),
    pedidos=("id_pedido","count")
).reset_index()

rentabilidad_cliente["ticket_promedio"] = (
    rentabilidad_cliente["ingresos"] /
    rentabilidad_cliente["pedidos"]
)

st.dataframe(
    rentabilidad_cliente.sort_values("ingresos", ascending=False),
    use_container_width=True
)

st.divider()

# =========================
# PUNTO DE EQUILIBRIO
# =========================

promedio_gastos = finanzas["monto"].mean()
pedidos_equilibrio = (
    promedio_gastos / ticket_promedio
) if ticket_promedio > 0 else 0

st.subheader("⚖️ Punto de Equilibrio")

st.metric("Pedidos necesarios para cubrir gastos promedio mensual",
          f"{pedidos_equilibrio:.0f}")

st.divider()

# =========================
# ALERTAS ESTRATÉGICAS
# =========================

st.subheader("🚨 Alertas Estratégicas")

#if margen_operativo < 15:
#    st.warning("Margen operativo bajo para empresa consolidada.")

if concentracion > 60:
    st.error("Alta dependencia de pocos clientes.")

if volatilidad > finanzas["total"].mean() * 0.4:
    st.warning("Alta volatilidad en ingresos mensuales.")

if ebitda < 0:
    st.error("La empresa está operando con pérdidas.")
