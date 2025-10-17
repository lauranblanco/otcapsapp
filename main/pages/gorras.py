import streamlit as st
import pandas as pd

def show():
    st.title("📊 Dashboard Principal")
    
    # Cargar datos
    df = pd.DataFrame() #load_data("Mi-Archivo-Excel")
    
    print('No tenemos datos aun')