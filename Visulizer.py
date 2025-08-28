import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Visualizador Tickets", page_icon="🎫", layout="wide")
st.title("🎫 Visualizador de Tickets")

# URL RAW del CSV en GitHub (ajusta con tu usuario y repo)
CSV_URL = "https://raw.githubusercontent.com/facility-coder/tickets-visualizer/main/data/tickets.csv"

@st.cache_data(ttl=60)
def cargar_csv(url):
    df = pd.read_csv(url, dtype=str, encoding="utf-8")
    df.columns = [str(c).strip() for c in df.columns]

    # Renombramos las columnas (orden correcto desde la 0 hasta la 24)
    df.columns = [
        "Ticket", "Unidad de Negocio", "Sociedad", "Área", "Fecha Solicitud",
        "Reporte", "Mes", "Prioridad", "Categoría", "Tipo",
        "Solicitado Por", "Tiempo Estimado", "Fecha Inicio",
        "Fecha Terminación", "Mes Terminación", "Ejecutado SLA",
        "Tiempo Vs Solicitado", "Días desde Solicitud", "Estado",
        "Ejecutor", "Presupuesto", "Materiales", "Link de Soporte", "Foto"
    ]

    # 👉 Ocultamos la primera columna (Ticket)
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

