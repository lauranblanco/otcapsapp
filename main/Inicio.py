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
facturas_df = pd.read_sql_query("SELECT * FROM facturas", conn)

pedidos_pendientes = pedidos_df[pedidos_df["estado"]=="pendiente"]
pedidos_entregados = pedidos_df[pedidos_df["estado"]=="entregado"]

atrasados = pd.read_sql_query("""
    SELECT 
        p.id_pedido,
        c.nombre as cliente,
        p.fecha_entrega,
        p.total
    FROM pedidos p
    JOIN clientes c ON p.id_cliente = c.id_cliente
    WHERE p.estado='pendiente'
    AND p.fecha_entrega < date('now')
    ORDER BY p.fecha_entrega ASC
""", conn)

# Facturas vencidas (impacto operativo)
facturas_vencidas = facturas_df[facturas_df["estado"]=="vencido"]

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

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Pedidos Pendientes", len(pedidos_pendientes))
col2.metric("Pedidos Atrasados", len(atrasados))
col3.metric("Facturas Vencidas", len(facturas_vencidas))
col4.metric("Promedio Días Entrega", f"{promedio_dias:.1f}")
col5.metric("Cumplimiento Entrega", f"{cumplimiento:.1f}%")

if len(atrasados) > 0:
    st.error("Hay pedidos fuera de tiempo.")

if len(facturas_vencidas) > 0:
    st.warning("Hay facturas vencidas que podrían afectar producción.")

st.divider()

# ==================================================
# 📊 2. ESTADO GENERAL (SE MANTIENE)
# ==================================================

total_ventas = pedidos_df["total"].sum()
gastos_totales = pd.read_sql_query(
    "SELECT IFNULL(SUM(monto),0) as total FROM gastos",
    conn
)["total"][0]

st.subheader("📊 Estado General")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Ventas Totales", f"${total_ventas:,.0f}")
col2.metric("Pedidos Entregados", len(pedidos_entregados))
col3.metric("Gastos Totales", f"${gastos_totales:,.0f}")
col4.metric("Pedidos Pendientes", len(pedidos_pendientes))

estado_df = pd.read_sql_query("""
    SELECT estado, COUNT(*) as cantidad
    FROM pedidos
    GROUP BY estado
""", conn)

st.bar_chart(estado_df.set_index("estado"))

st.divider()

# ==================================================
# 🚚 3. PRÓXIMAS ENTREGAS (SE MANTIENE)
# ==================================================

st.subheader("🚚 Próximas Entregas")

proximos = pd.read_sql_query("""
    SELECT 
        p.id_pedido,
        c.nombre as cliente,
        p.fecha_entrega,
        p.total
    FROM pedidos p
    JOIN clientes c ON p.id_cliente = c.id_cliente
    WHERE p.estado='pendiente'
    ORDER BY p.fecha_entrega ASC
    LIMIT 10
""", conn)

st.dataframe(proximos, use_container_width=True)

st.divider()

# ==================================================
# 📈 4. CARGA OPERATIVA Y TENDENCIA (SE MANTIENE)
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
merged["utilidad"] = merged["ventas"] - merged["gastos"]

st.line_chart(merged.set_index("mes")[["ventas","gastos","utilidad"]])

st.divider()

# ==================================================
# 👥 5. CLIENTES MÁS ACTIVOS (SE MANTIENE)
# ==================================================

st.subheader("👥 Clientes Más Activos (Mes Actual)")

clientes_mes = pd.read_sql_query("""
    SELECT 
        c.nombre as cliente,
        COUNT(*) as pedidos
    FROM pedidos p
    JOIN clientes c ON p.id_cliente = c.id_cliente
    WHERE strftime('%Y-%m', p.fecha_entrega)=strftime('%Y-%m','now')
    GROUP BY c.nombre
    ORDER BY pedidos DESC
    LIMIT 5
""", conn)

st.dataframe(clientes_mes, use_container_width=True)

st.divider()

# ==================================================
# 📦 6. INSUMOS MÁS UTILIZADOS (SE MANTIENE)
# ==================================================

st.subheader("📦 Insumos Más Utilizados")

insumos = pd.read_sql_query("""
    SELECT 
        i.nombre as insumo,
        SUM(d.cantidad) as total_usado
    FROM detalle_pedido d
    JOIN insumos i ON d.id_insumo = i.id_insumo
    GROUP BY i.nombre
    ORDER BY total_usado DESC
    LIMIT 5
""", conn)

st.dataframe(insumos, use_container_width=True)

st.divider()

# ==================================================
# 🧾 7. NUEVO: ESTADO DE COBRANZA POR PEDIDO
# ==================================================

st.subheader("🧾 Estado de Cobranza de Pedidos")

cobranza = pd.read_sql_query("""
    SELECT 
        p.id_pedido,
        c.nombre as cliente,
        p.total,
        IFNULL(SUM(f.monto),0) as facturado,
        p.total - IFNULL(SUM(f.monto),0) as pendiente
    FROM pedidos p
    JOIN clientes c ON p.id_cliente = c.id_cliente
    LEFT JOIN facturas f ON p.id_pedido = f.id_pedido 
        AND f.estado='pagado'
    GROUP BY p.id_pedido
    ORDER BY pendiente DESC
""", conn)

st.dataframe(cobranza, use_container_width=True)

st.divider()

# ==================================================
# 🚨 8. ALERTAS OPERATIVAS (SE MANTIENE + MEJORA)
# ==================================================

st.subheader("🚨 Alertas Operativas")

if promedio_dias > 15:
    st.warning("Tiempo promedio de entrega elevado.")

if len(pedidos_pendientes) > 20:
    st.warning("Alta acumulación de pedidos pendientes.")

if len(atrasados) > 5:
    st.error("Exceso de pedidos atrasados.")

if len(facturas_vencidas) > 0:
    st.warning("Cartera vencida puede frenar operación.")

