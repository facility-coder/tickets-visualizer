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
    df = pd.read_csv(url, dtype=str, encoding="utf-8", skiprows=3)
    df.columns = [str(c).strip() for c in df.columns]

    # 👉 Renombramos dinámicamente las columnas
    mapping = {
        df.columns[0]:  "Ticket",
        df.columns[1]:  "Unidad de Negocio",
        df.columns[2]:  "Sociedad",
        df.columns[3]:  "Área",
        df.columns[4]:  "Fecha Solicitud",
        df.columns[5]:  "Reporte",
        df.columns[6]:  "Mes",
        df.columns[7]:  "Prioridad",
        df.columns[8]:  "Categoría",
        df.columns[9]:  "Tipo",
        df.columns[10]: "Solicitado Por",
        df.columns[11]: "Tiempo Estimado",
        df.columns[12]: "Fecha Inicio",
        df.columns[13]: "Fecha Terminación",
        df.columns[14]: "Mes Terminación",
        df.columns[15]: "Ejecutado SLA",
        df.columns[16]: "Tiempo Vs Solicitado",
        df.columns[17]: "Días desde Solicitud",
        df.columns[18]: "Estado",
        df.columns[19]: "Ejecutor",
        df.columns[20]: "Presupuesto",
        df.columns[21]: "Materiales",
        df.columns[22]: "Link de Soporte",
        df.columns[23]: "Foto"
    }
    df = df.rename(columns=mapping)

    # 👉 Ocultar columna 0 (Ticket)
    df = df.iloc[:, 1:]
    return df

try:
    df = cargar_csv(CSV_URL)
    st.success(f"✅ Cargado: {len(df)} filas × {len(df.columns)} columnas")
    st.dataframe(df, use_container_width=True, height=600)
    st.caption(f"Última actualización: {datetime.now():%Y-%m-%d %H:%M:%S}")

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

    st.dataframe(view, use_container_width=True, height=400)

    # -------------------------------
    # ⬇️ Descargar CSV filtrado
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
