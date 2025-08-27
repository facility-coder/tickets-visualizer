import streamlit as st
import pandas as pd
from datetime import datetime

# ---------------------------
# Configuración de la página
# ---------------------------
st.set_page_config(page_title="Visualizador de Tickets", page_icon="🎫", layout="wide")
st.title("🎫 Visualizador de Tabla_Principal")

# ---------------------------
# Cargar datos del Excel
# ---------------------------
@st.cache_data(ttl=30)  # refresca cache cada 30 segundos
def cargar_tabla(ruta_excel, hoja="Tabla Principal (Correctivo)"):
    return pd.read_excel(ruta_excel, sheet_name=hoja, engine="openpyxl", dtype=str)

ruta = r"C:/Users/Albel/Desktop/Script/Mantenimiento Correctivo 2025.xlsm"  # ajusta tu ruta
df = cargar_tabla(ruta, "Tabla Principal (Correctivo)")

# ---------------------------
# Mostrar la tabla completa
# ---------------------------
st.dataframe(df, use_container_width=True, height=600)

st.info(f"📅 Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ---------------------------
# Botón para refrescar manualmente
# ---------------------------
if st.button("🔄 Actualizar ahora"):
    st.cache_data.clear()
    st.rerun()