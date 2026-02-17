import streamlit as st
import pandas as pd
import sqlite3
from db import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)

st.set_page_config(page_title="Resumen Operativo", layout="wide")
st.title("🏭 Resumen Operativo")

conn = get_connection()

# ==================================================
# CARGA BASE
# ==================================================

pedidos_df = pd.read_sql_query("SELECT * FROM pedidos", conn)
facturas_df = pd.read_sql_query("SELECT * FROM facturas", conn)

if pedidos_df.empty:
    st.warning("No hay pedidos registrados.")
    st.stop()

# ==================================================
# 1️⃣ SITUACIÓN CRÍTICA (PRIORIDAD ABSOLUTA)
# ==================================================

st.subheader("🔴 Situación Crítica")

# Pedidos pendientes
pendientes = pedidos_df[pedidos_df["estado"] == "pendiente"]

# Pedidos atrasados
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

# Facturas vencidas (impacta operación)
facturas_vencidas = facturas_df[
    facturas_df["estado"] == "vencido"
]

col1, col2, col3 = st.columns(3)

col1.metric("Pedidos Pendientes", len(pendientes))
col2.metric("Pedidos Atrasados", len(atrasados))
col3.metric("Facturas Vencidas", len(facturas_vencidas))

if len(atrasados) > 0:
    st.error("Hay pedidos fuera de tiempo.")

if len(facturas_vencidas) > 0:
    st.warning("Existen facturas vencidas que pueden afectar producción.")

st.divider()

# ==================================================
# 2️⃣ EFICIENCIA OPERATIVA
# ==================================================

st.subheader("⚙️ Eficiencia Operativa")

# Tiempo promedio entrega
tiempos = pd.read_sql_query("""
    SELECT julianday(fecha_entrega) - julianday(fecha_anticipo) as dias
    FROM pedidos
    WHERE estado='entregado'
""", conn)

promedio_dias = tiempos["dias"].mean() if not tiempos.empty else 0

# Cumplimiento %
total_entregados = len(pedidos_df[pedidos_df["estado"]=="entregado"])

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

col1, col2 = st.columns(2)

col1.metric("Promedio Días Entrega", f"{promedio_dias:.1f}")
col2.metric("Cumplimiento Entrega", f"{cumplimiento:.1f}%")

if cumplimiento < 80:
    st.warning("Nivel de cumplimiento bajo.")

st.divider()

# ==================================================
# 3️⃣ PRÓXIMAS ENTREGAS (PLANIFICACIÓN)
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
# 4️⃣ CARGA OPERATIVA FUTURA
# ==================================================

st.subheader("📈 Carga Operativa por Semana")

carga = pd.read_sql_query("""
    SELECT strftime('%Y-%W', fecha_entrega) as semana,
           COUNT(*) as pedidos
    FROM pedidos
    WHERE estado='pendiente'
    GROUP BY semana
    ORDER BY semana
""", conn)

st.bar_chart(carga.set_index("semana"))

st.divider()

# ==================================================
# 5️⃣ ESTADO GENERAL DE PEDIDOS
# ==================================================

st.subheader("📊 Distribución de Estados")

estado_df = pd.read_sql_query("""
    SELECT estado, COUNT(*) as cantidad
    FROM pedidos
    GROUP BY estado
""", conn)

st.bar_chart(estado_df.set_index("estado"))

st.divider()

# ==================================================
# 6️⃣ CLIENTES MÁS ACTIVOS (MES ACTUAL)
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
# 7️⃣ INSUMOS MÁS UTILIZADOS
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
# 8️⃣ ALERTAS OPERATIVAS AUTOMÁTICAS
# ==================================================

st.subheader("🚨 Alertas Operativas")

if promedio_dias > 15:
    st.warning("Tiempo promedio de entrega elevado.")

if len(pendientes) > 20:
    st.warning("Alta acumulación de pedidos pendientes.")

if len(atrasados) > 5:
    st.error("Exceso de pedidos atrasados.")

