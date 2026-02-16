import streamlit as st
from db_init import init_db
from db import get_connection
import pandas as pd

init_db()  # asegura que las tablas existan

st.title("Test conexión SQLite 🚀")

conn = get_connection()

# Insert test
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

if st.button("Insertar insumo prueba"):
    conn.execute(
        "INSERT INTO insumos (nombre) VALUES (?)",
        ("insumo",)
    )
    conn.commit()
    st.success("Insumo insertado")

# Mostrar tabla
df = pd.read_sql("SELECT * FROM insumos", conn)
st.dataframe(df)