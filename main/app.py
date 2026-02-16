import streamlit as st
from db_init import init_db
from db import get_connection
import pandas as pd

init_db()  # asegura que las tablas existan

st.title("Test conexión SQLite 🚀")

conn = get_connection()

# Insert test
st.subheader("Test clientes")
if st.button("Insertar cliente prueba"):
    conn.execute(
        "INSERT INTO clientes (nombre) VALUES (?)",
        ("Laura Test",)
    )
    conn.commit()
    st.success("Cliente insertado")

# Mostrar tabla
df = pd.read_sql("SELECT * FROM clientes", conn)
st.dataframe(df)

st.subheader("Test insumos")
if st.button("Insertar insumo prueba"):
    conn.execute(
        "INSERT INTO insumos (nombre, costo_unitario) VALUES (?, ?)",
        ("insumo", 10.0)
    )
    conn.commit()
    st.success("Insumo insertado")

# Mostrar tabla
df1 = pd.read_sql("SELECT * FROM insumos", conn)
st.dataframe(df1)

st.subheader("Test pedidos")
df2 = pd.read_sql("SELECT * FROM pedidos", conn)
st.dataframe(df2)

st.subheader("Test detalle pedido")
df3 = pd.read_sql("SELECT * FROM detalle_pedido", conn)
st.dataframe(df3)