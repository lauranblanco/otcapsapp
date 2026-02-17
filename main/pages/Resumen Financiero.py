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
# CARGA DE DATOS
# =========================

pedidos_df = pd.read_sql_query("""
    SELECT * FROM pedidos
    WHERE estado != 'cancelado'
""", conn)

gastos_df = pd.read_sql_query("SELECT * FROM gastos", conn)
clientes_df = pd.read_sql_query("SELECT * FROM clientes", conn)
facturas_df = pd.read_sql_query("SELECT * FROM facturas", conn)

if pedidos_df.empty:
    st.warning("No hay datos de pedidos registrados.")
    st.stop()

# =========================
# MÉTRICAS FINANCIERAS REALES
# =========================

ventas_devengadas = pedidos_df["total"].sum()

cobros_reales = facturas_df.loc[
    facturas_df["estado"] == "pagado", "monto"
].sum()

cuentas_por_cobrar = facturas_df.loc[
    facturas_df["estado"] == "pendiente", "monto"
].sum()

cartera_vencida = facturas_df.loc[
    facturas_df["estado"] == "vencido", "monto"
].sum()

gastos_totales = gastos_df["monto"].sum()

utilidad_devengada = ventas_devengadas - gastos_totales
flujo_caja_real = cobros_reales - gastos_totales

ticket_promedio = pedidos_df["total"].mean()

# =========================
# 1️⃣ LIQUIDEZ (PRIORIDAD EJECUTIVA)
# =========================

st.subheader("💵 Liquidez y Flujo de Caja")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Cobros Reales", f"${cobros_reales:,.0f}")
col2.metric("Cuentas por Cobrar", f"${cuentas_por_cobrar:,.0f}")
col3.metric("Cartera Vencida", f"${cartera_vencida:,.0f}")
col4.metric("Flujo Caja Neto", f"${flujo_caja_real:,.0f}")

# Calidad de cobranza
if ventas_devengadas > 0:
    ratio_cobranza = (cobros_reales / ventas_devengadas) * 100
else:
    ratio_cobranza = 0

st.metric("Ratio de Cobranza", f"{ratio_cobranza:.1f}%")

if ratio_cobranza < 60:
    st.error("Problema grave de cobranza.")
elif ratio_cobranza < 80:
    st.warning("Cobranza moderada.")
else:
    st.success("Cobranza saludable.")

st.divider()

# =========================
# 2️⃣ RENTABILIDAD
# =========================

st.subheader("📊 Rentabilidad")

col1, col2, col3 = st.columns(3)

col1.metric("Ventas Devengadas", f"${ventas_devengadas:,.0f}")
col2.metric("Gastos Totales", f"${gastos_totales:,.0f}")
col3.metric("Utilidad Devengada", f"${utilidad_devengada:,.0f}")

margen_operativo = (utilidad_devengada / ventas_devengadas * 100) if ventas_devengadas > 0 else 0
st.metric("Margen Operativo", f"{margen_operativo:.1f}%")

st.divider()

# =========================
# 3️⃣ FLUJO DE CAJA MENSUAL
# =========================

st.subheader("📈 Flujo de Caja Mensual")

facturas_pagadas = facturas_df[facturas_df["estado"] == "pagado"].copy()

if not facturas_pagadas.empty:
    facturas_pagadas["mes"] = pd.to_datetime(
        facturas_pagadas["fecha_pago"]
    ).dt.to_period("M")

    gastos_df["mes"] = pd.to_datetime(
        gastos_df["fecha"]
    ).dt.to_period("M")

    cobros_mes = facturas_pagadas.groupby("mes")["monto"].sum().reset_index()
    gastos_mes = gastos_df.groupby("mes")["monto"].sum().reset_index()

    flujo = pd.merge(cobros_mes, gastos_mes, on="mes", how="left").fillna(0)
    flujo["flujo_neto"] = flujo["monto_x"] - flujo["monto_y"]

    st.line_chart(
        flujo.set_index("mes")[["monto_x","flujo_neto"]]
    )
else:
    st.info("Aún no hay facturas pagadas registradas.")

st.divider()

# =========================
# 4️⃣ CONCENTRACIÓN DE INGRESOS
# =========================

st.subheader("🏆 Concentración de Ingresos")

cliente_ingresos = pd.read_sql_query("""
    SELECT 
        c.nombre as cliente,
        SUM(p.total) as ingresos
    FROM pedidos p
    JOIN clientes c ON p.id_cliente = c.id_cliente
    WHERE p.estado != 'cancelado'
    GROUP BY c.nombre
    ORDER BY ingresos DESC
""", conn)

cliente_ingresos["participacion_%"] = (
    cliente_ingresos["ingresos"] / ventas_devengadas * 100
)

top_3 = cliente_ingresos.head(3)["ingresos"].sum()
concentracion = (top_3 / ventas_devengadas) * 100 if ventas_devengadas > 0 else 0

col1, col2 = st.columns([1,2])

col1.metric("Dependencia Top 3", f"{concentracion:.1f}%")

col2.dataframe(
    cliente_ingresos.head(5).rename(columns={
        "cliente": "Cliente",
        "ingresos": "Ingresos",
        "participacion_%": "% Participación"
    }),
    use_container_width=True
)

st.divider()

# =========================
# 5️⃣ RENTABILIDAD POR CLIENTE
# =========================

st.subheader("💎 Rentabilidad por Cliente")

rentabilidad_cliente = pd.read_sql_query("""
    SELECT 
        c.nombre as cliente,
        COUNT(p.id_pedido) as pedidos,
        SUM(p.total) as ingresos
    FROM pedidos p
    JOIN clientes c ON p.id_cliente = c.id_cliente
    WHERE p.estado != 'cancelado'
    GROUP BY c.nombre
    ORDER BY ingresos DESC
""", conn)

rentabilidad_cliente["ticket_promedio"] = (
    rentabilidad_cliente["ingresos"] /
    rentabilidad_cliente["pedidos"]
)

st.dataframe(rentabilidad_cliente, use_container_width=True)

st.divider()

# =========================
# 6️⃣ PUNTO DE EQUILIBRIO
# =========================

promedio_gastos = gastos_totales / 12 if gastos_totales > 0 else 0
pedidos_equilibrio = (
    promedio_gastos / ticket_promedio
) if ticket_promedio > 0 else 0

st.subheader("⚖️ Punto de Equilibrio")

st.metric(
    "Pedidos necesarios para cubrir gasto promedio mensual",
    f"{pedidos_equilibrio:.0f}"
)

st.divider()

# =========================
# 7️⃣ ALERTAS ESTRATÉGICAS
# =========================

st.subheader("🚨 Alertas Estratégicas")

if cartera_vencida > 0:
    st.error("Existen facturas vencidas.")

if concentracion > 60:
    st.warning("Alta dependencia de pocos clientes.")

if margen_operativo < 15:
    st.warning("Margen operativo bajo.")

if flujo_caja_real < 0:
    st.error("Flujo de caja negativo.")
