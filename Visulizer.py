import streamlit as st
import pandas as pd
from datetime import datetime

# ---------------------------
# Configuración de la página
# ---------------------------
st.set_page_config(
    page_title="Visualizador de Tickets",
    page_icon="🎫",
    layout="wide"
)

st.title("🎫 Visualizador de Tabla_Principal")

# ---------------------------
# URL del Excel en OneDrive
# ---------------------------
# IMPORTANTE: Genera un link de descarga directa desde OneDrive
# ejemplo: https://onedrive.live.com/download?cid=XXXXXXX&resid=XXXXXXX
url = "https://yrfda-my.sharepoint.com/:x:/g/personal/hector_hernandez_yrfda_onmicrosoft_com/EU5O1TEO_npMo59ye00akMsBwTb-Y4aOH3Y86LlvSrvbJg?e=DvBQji"

# ---------------------------
# Cargar datos
# ---------------------------
@st.cache_data(ttl=60)  # refresca cada 60 segundos
def cargar_tabla(url, hoja="Tabla Principal (Correctivo)"):
    return pd.read_excel(url, sheet_name=hoja, engine="openpyxl", dtype=str)

try:
    df = cargar_tabla(url)
    st.success(f"✅ Datos cargados correctamente ({len(df)} filas, {len(df.columns)} columnas)")

    # Mostrar la tabla completa
    st.dataframe(df, use_container_width=True, height=600)

    # Info de actualización
    st.caption(f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Botón para refrescar manualmente
    if st.button("🔄 Actualizar ahora"):
        st.cache_data.clear()
        st.rerun()

    # Descargar CSV filtrado
    st.subheader("⬇️ Descargar datos")
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("Descargar CSV", data=csv, file_name="tickets.csv", mime="text/csv")

except Exception as e:
    st.error(f"❌ No se pudo cargar la tabla: {e}")

    st.info("Verifica que el link de OneDrive sea correcto y que tengas permisos de lectura.")
