import re
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Visualizador Tickets", page_icon="🎫", layout="wide")
st.title("🎫 Visualizador de Tickets")

# URL RAW del CSV en GitHub
CSV_URL = "https://raw.githubusercontent.com/facility-coder/tickets-visualizer/main/data/tickets.csv"

def _parse_money_series(s: pd.Series) -> pd.Series:
    """
    Convierte strings de dinero a float manejando formatos:
    - "B/. 1,234.56"  -> 1234.56
    - "1.234,56"      -> 1234.56
    - "1,234"         -> 1234.00
    - valores vacíos  -> NaN
    """
    s = s.astype(str).str.replace(r"[^\d\.,\-]", "", regex=True).str.strip()

    def _to_float(x: str):
        if not x or x.lower() in {"nan", "none"}:
            return None
        # ambos separadores
        if "," in x and "." in x:
            # si la última coma está a la derecha del último punto -> coma decimal (formato europeo)
            if x.rfind(",") > x.rfind("."):
                x = x.replace(".", "").replace(",", ".")
            else:
                # formato en-US: coma miles, punto decimal
                x = x.replace(",", "")
        else:
            # solo comas
            if "," in x and "." not in x:
                # asumimos coma decimal
                x = x.replace(",", ".")
            else:
                # solo puntos o ninguno -> quitar separador de miles si hubiese comas
                x = x.replace(",", "")
        try:
            return float(x)
        except Exception:
            return None

    return s.apply(_to_float)

@st.cache_data(ttl=60)
def cargar_csv(url):
    # 👇 Saltamos las 3 primeras filas
    df = pd.read_csv(url, dtype=str, encoding="utf-8", skiprows=3, on_bad_lines="skip")
    df.columns = [str(c).strip() for c in df.columns]

    # 👉 Renombramos dinámicamente las columnas (primeras 24 si existen)
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

    # ✅ Dejar Ticket visible (no ocultamos)

    # 🔁 Parsear Presupuesto a número (si existe)
    if "Presupuesto" in df.columns:
        df["Presupuesto"] = _parse_money_series(df["Presupuesto"])

    return df

try:
    df = cargar_csv(CSV_URL)
    st.success(f"✅ Cargado: {len(df)} filas × {len(df.columns)} columnas")
    st.caption(f"Última actualización: {datetime.now():%Y-%m-%d %H:%M:%S}")

    # ----- Tabla completa con índice que empieza en 1 -----
    df_display = df.copy()
    df_display.index = range(1, len(df_display) + 1)
    df_display.index.name = "N°"

    # Configuración de columnas (formato Balboa para Presupuesto)
    col_config = {}
    if "Presupuesto" in df_display.columns:
        col_config["Presupuesto"] = st.column_config.NumberColumn(
            "Presupuesto (B/.)",
            format="B/. %,.2f"
        )

    st.dataframe(
        df_display,
        use_container_width=True,
        height=600,
        column_config=col_config
    )

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

    # ----- Tabla filtrada con índice que empieza en 1 -----
    view_display = view.copy()
    view_display.index = range(1, len(view_display) + 1)
    view_display.index.name = "N°"

    col_config_view = {}
    if "Presupuesto" in view_display.columns:
        col_config_view["Presupuesto"] = st.column_config.NumberColumn(
            "Presupuesto (B/.)",
            format="B/. %,.2f"
        )

    st.dataframe(
        view_display,
        use_container_width=True,
        height=400,
        column_config=col_config_view
    )

    # -------------------------------
    # ⬇️ Descargar CSV filtrado (sin índice)
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
    st.info("Verifica que el archivo tickets.csv exista en GitHub.")


