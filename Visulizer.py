import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Visualizador Tickets", page_icon="🎫", layout="wide")
st.title("🎫 Visualizador de Tickets")

# URL RAW del CSV en GitHub
CSV_URL = "https://raw.githubusercontent.com/facility-coder/tickets-visualizer/main/data/tickets.csv"

@st.cache_data(ttl=60)
def cargar_csv(url: str) -> pd.DataFrame:
    # Saltamos las 3 primeras filas y evitamos romper por líneas defectuosas
    df = pd.read_csv(url, dtype=str, encoding="utf-8", skiprows=3, on_bad_lines="skip")

    # Quitar columnas completamente vacías (a veces Excel deja columnas extra)
    df = df.dropna(axis=1, how="all")

    # Limpiar encabezados
    df.columns = [str(c).strip() for c in df.columns]

    # Renombrado dinámico solo hasta donde existan columnas
    nuevos = [
        "Ticket", "Unidad de Negocio", "Sociedad", "Área", "Fecha Solicitud",
        "Reporte", "Mes", "Prioridad", "Categoría", "Tipo",
        "Solicitado Por", "Tiempo Estimado", "Fecha Inicio",
        "Fecha Terminación", "Mes Terminación", "Ejecutado SLA",
        "Tiempo Vs Solicitado", "Días desde Solicitud", "Estado",
        "Ejecutor", "Presupuesto", "Materiales", "Link de Soporte", "Foto"
    ]
    n = min(len(df.columns), len(nuevos))
    mapping = {df.columns[i]: nuevos[i] for i in range(n)}
    df = df.rename(columns=mapping)

    # Usar Ticket como índice (si no existe, usar la primera columna como índice y llamarla Ticket)
    if "Ticket" in df.columns:
        df = df.set_index("Ticket")
    else:
        first_col = df.columns[0]
        df = df.set_index(first_col)
        df.index.name = "Ticket"

    return df

try:
    df = cargar_csv(CSV_URL)
    st.success(f"✅ Cargado: {len(df)} filas × {len(df.columns)} columnas")
    st.caption(f"Última actualización: {datetime.now():%Y-%m-%d %H:%M:%S}")

    # -------------------------------
    # 🔎 Búsqueda rápida (incluye índice Ticket)
    # -------------------------------
    st.subheader("🔎 Buscar")
    opciones_cols = ["(todas)", "Ticket (índice)"] + list(df.columns)
    col = st.selectbox("Columna", opciones_cols)
    q = st.text_input("Texto contiene:", "")

    view = df
    if q:
        q_norm = str(q)
        if col == "(todas)":
            # Busca en todas las columnas + índice
            mask_cols = False
            for c in df.columns:
                mask_cols = mask_cols | df[c].astype(str).str.contains(q_norm, case=False, na=False)
            mask_index = df.index.astype(str).str.contains(q_norm, case=False, na=False)
            view = df[mask_cols | mask_index]
        elif col == "Ticket (índice)":
            view = df[df.index.astype(str).str.contains(q_norm, case=False, na=False)]
        else:
            view = df[df[col].astype(str).str.contains(q_norm, case=False, na=False)]

        st.info(f"Coincidencias: {len(view)}")

    # Tabla principal
    st.dataframe(view, use_container_width=True, height=600)

    # -------------------------------
    # ⬇️ Descargar CSV filtrado (con Ticket como columna)
    # -------------------------------
    st.download_button(
        "⬇️ Descargar CSV filtrado",
        data=view.reset_index().to_csv(index=False).encode("utf-8-sig"),
        file_name="tickets_filtrados.csv",
        mime="text/csv"
    )

    # -------------------------------
    # 🔄 Botón para refrescar manualmente
    # -------------------------------
    if st.button("🔄 Refrescar ahora"):
        st.cache_data.clear()
        st.rerun()

except Exception as e:
    st.error(f"❌ No se pudo cargar el CSV: {e}")
    st.info("Verifica la URL RAW en GitHub y el formato del archivo.")
