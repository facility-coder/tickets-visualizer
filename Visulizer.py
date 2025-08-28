import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Visualizador Tickets", page_icon="🎫", layout="wide")
st.title("🎫 Visualizador de Tickets")

# URL RAW del CSV en GitHub
CSV_URL = "https://raw.githubusercontent.com/facility-coder/tickets-visualizer/main/data/tickets.csv"

@st.cache_data(ttl=60)
def cargar_csv(url):
    # 👇 Saltamos las 3 primeras filas
    df = pd.read_csv(url, dtype=str, encoding="utf-8", skiprows=4)
    df.columns = [str(c).strip() for c in df.columns]

    # 👉 Renombramos dinámicamente las columnas
    mapping = {
        df.columns[1]:  "Ticket",
        df.columns[2]:  "Unidad de Negocio",
        df.columns[3]:  "Sociedad",
        df.columns[4]:  "Área",
        df.columns[5]:  "Fecha Solicitud",
        df.columns[6]:  "Reporte",
        df.columns[7]:  "Mes",
        df.columns[8]:  "Prioridad",
        df.columns[9]:  "Categoría",
        df.columns[10]:  "Tipo",
        df.columns[11]: "Solicitado Por",
        df.columns[12]: "Tiempo Estimado",
        df.columns[13]: "Fecha Inicio",
        df.columns[14]: "Fecha Terminación",
        df.columns[15]: "Mes Terminación",
        df.columns[16]: "Ejecutado SLA",
        df.columns[17]: "Tiempo Vs Solicitado",
        df.columns[18]: "Días desde Solicitud",
        df.columns[19]: "Tiempo Terminado Vs solicitado2",
        df.columns[20]: "Estado",
        df.columns[21]: "Ejecutor",
        df.columns[22]: "Presupuesto",
        df.columns[23]: "Materiales",
        df.columns[24]: "Link de Soporte",
        df.columns[25]: "Foto"
    }
    df = df.rename(columns=mapping)

    # ✅ Dejamos Ticket visible (no lo ocultamos)
    return df

try:
    df = cargar_csv(CSV_URL)
    st.success(f"✅ Cargado: {len(df)} filas × {len(df.columns)} columnas")
    st.caption(f"Última actualización: {datetime.now():%Y-%m-%d %H:%M:%S}")

    # ----- Tabla completa con índice empezando en 1 -----
    df_display = df.copy()
    df_display.index = range(1, len(df_display) + 1)
    df_display.index.name = "N°"
    st.dataframe(df_display, use_container_width=True, height=600)

    # -------------------------------
    # 🔎 Búsqueda rápida
    # -------------------------------
    st.subheader("🔎 Buscar")
    col = st.selectbox("Columna", ["(todas)"] + list(df.columns))
    q = st.text_input("Texto contiene:", "")

    view = df
    if q:
        if col == "(todas)":
            mask = False
            for c in df.columns:
                mask = mask | df[c].astype(str).str.contains(q, case=False, na=False)
            view = df[mask]
        else:
            view = df[df[col].astype(str).str.contains(q, case=False, na=False)]
        st.info(f"Coincidencias: {len(view)}")

    # ----- Tabla filtrada con índice empezando en 1 -----
    view_display = view.copy()
    view_display.index = range(1, len(view_display) + 1)
    view_display.index.name = "N°"
    st.dataframe(view_display, use_container_width=True, height=400)

    # -------------------------------
    # ⬇️ Descargar CSV filtrado (sin índice)
    # -------------------------------
    st.download_button("⬇️ Descargar CSV filtrado",
                       data=view.to_csv(index=False).encode("utf-8-sig"),
                       file_name="tickets_filtrados.csv",
                       mime="text/csv")

    # -------------------------------
    # 🔄 Botón para refrescar manualmente
    # -------------------------------
    if st.button("🔄 Refrescar ahora"):
        st.cache_data.clear()
        st.rerun()

except Exception as e:
    st.error(f"❌ No se pudo cargar el CSV: {e}")
    st.info("Verifica que el archivo tickets.csv exista en GitHub.")


