import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Visualizador Tickets", page_icon="🎫", layout="wide")
st.title("🎫 Visualizador de Tickets")

# URL RAW del CSV en GitHub
CSV_URL = "https://raw.githubusercontent.com/facility-coder/tickets-visualizer/main/data/tickets.csv"

# CSS para animación de parpadeo
st.markdown("""
<style>
@keyframes pulse-red {
  0%   { background-color:#ff4d4f; }
  50%  { background-color:#ffb3b3; }
  100% { background-color:#ff4d4f; }
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def cargar_csv(url):
    # 👇 Saltamos las 3 primeras filas del CSV
    df = pd.read_csv(url, dtype=str, encoding="utf-8", skiprows=3)
    df.columns = [str(c).strip() for c in df.columns]

    # 👉 Renombramos dinámicamente las primeras 24 columnas (si existen)
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

    # 👉 Ocultamos la primera columna (Ticket) si existe; si no, quitamos la col 0
    if "Ticket" in df.columns:
        df = df.drop(columns=["Ticket"])
    else:
        df = df.iloc[:, 1:]

    return df

def estilizar_blink(view: pd.DataFrame, estados_objetivo, umbral_dias: int):
    # Función para aplicar estilos por fila
    def _row_style(row):
        estado = str(row.get("Estado", "")).strip().lower()
        dias = pd.to_numeric(row.get("Días desde Solicitud", None), errors="coerce")
        is_crit = estado in estados_objetivo
        is_over = (dias >= umbral_dias) if pd.notna(dias) else False

        if is_crit or is_over:
            return ['color:white; background-color:#ff4d4f; animation:pulse-red 1s ease-in-out infinite;'] * len(row)
        else:
            return [''] * len(row)

    # Si faltan las columnas, solo devuelve la vista sin estilo
    if "Estado" not in view.columns and "Días desde Solicitud" not in view.columns:
        return view

    return view.style.apply(_row_style, axis=1)

try:
    df = cargar_csv(CSV_URL)
    st.success(f"✅ Cargado: {len(df)} filas × {len(df.columns)} columnas")
    st.caption(f"Última actualización: {datetime.now():%Y-%m-%d %H:%M:%S}")

    # -------------------------------
    # 🎛️ Controles
    # -------------------------------
    st.subheader("🎛️ Controles")
    # Filtro rápido
    col = st.selectbox("Filtrar por columna", ["(todas)"] + list(df.columns))
    q = st.text_input("Texto contiene:", "")

    # Parámetros de resaltado
    estados_default = {"Sin realizar"}
    estados_input = st.text_input(
        "Estados críticos (separados por coma)",
        value="Sin realizar"
    )
    estados_objetivo = {e.strip().lower() for e in estados_input.split(",") if e.strip()}
    if not estados_objetivo:
        estados_objetivo = estados_default

    umbral = st.number_input("Umbral de días para parpadeo", min_value=0, value=7, step=1)

    # -------------------------------
    # 🔎 Aplicar filtro
    # -------------------------------
    view = df
    if q:
        if col == "(todas)":
            mask = False
            for c in df.columns:
                mask = mask | df[c].astype(str).str.contains(q, case=False, na=False)
            view = df[mask]
        else:
            view = df[df[col].astype(str).str.contains(q, case=False, na=False)]

    st.info(f"Filas mostradas: {len(view)}")

    # -------------------------------
    # ✨ Tabla con parpadeo en rojo
    # -------------------------------
    styled = estilizar_blink(view, estados_objetivo, umbral)

    # Render de la tabla con estilo (si es Styler) o sin estilo (DataFrame)
    if isinstance(styled, pd.io.formats.style.Styler):
        # Nota: algunos entornos requieren st.write para Styler
        st.write(styled)
    else:
        st.dataframe(styled, use_container_width=True, height=500)

    # -------------------------------
    # ⬇️ Descargar CSV filtrado (sin Ticket y con 3 filas ocultas ya aplicado)
    # -------------------------------
    st.download_button(
        "⬇️ Descargar CSV filtrado",
        data=view.to_csv(index=False).encode("utf-8-sig"),
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
    st.info("Verifica que la URL sea correcta y el CSV exista en GitHub.")


