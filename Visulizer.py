import re
import unicodedata
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Visualizador Tickets", page_icon="🎫", layout="wide")
st.title("🎫 Visualizador de Tickets")

CSV_URL = "https://raw.githubusercontent.com/facility-coder/tickets-visualizer/main/data/tickets.csv"

# --- Helpers de normalización y mapeo ----------------------------------------
def _strip_accents(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn")

def _normalize_header(s: str) -> str:
    """ lower, sin acentos, sin paréntesis/ dd/mm/aa, solo letras/números/espacios """
    s = str(s or "").strip()
    s = re.sub(r"^unnamed.*$", "", s, flags=re.I)     # descartar 'Unnamed'
    s = _strip_accents(s).lower()
    s = re.sub(r"\(.*?\)", " ", s)                    # quita paréntesis (ej. (dd/mm/aa))
    s = re.sub(r"dd/?mm/?aa", " ", s)                 # remueve marcador de fecha
    s = re.sub(r"[^a-z0-9]+", " ", s)                 # deja solo alfanum/esp
    s = re.sub(r"\s+", " ", s).strip()
    return s

# Orden “canónico” de salida
PREFERRED_ORDER = [
    "Ticket", "Unidad de Negocio", "Sociedad", "Área", "Fecha Solicitud",
    "Reporte", "Mes", "Prioridad", "Categoría", "Tipo",
    "Solicitado Por", "Tiempo Estimado", "Fecha Inicio",
    "Fecha Terminación", "Mes Terminación", "Ejecutado SLA",
    "Tiempo Vs Solicitado", "Días desde Solicitud", "Estado",
    "Ejecutor", "Presupuesto", "Materiales", "Link de Soporte", "Foto"
]

# Sinónimos (términos normalizados) para detectar cada columna
SYNONYMS = {
    "Ticket": {
        "ticket", "nro ticket", "no ticket", "numero ticket", "# ticket", "n ticket"
    },
    "Unidad de Negocio": {
        "unidad de negocio", "unidad negocio", "udn"
    },
    "Sociedad": {"sociedad", "empresa", "compania", "company"},
    "Área": {"area"},
    "Fecha Solicitud": {"fecha solicitud", "fecha de solicitud", "fecha solicitud dia"},
    "Reporte": {"reporte", "descripcion", "descripcion del reporte", "detalle"},
    "Mes": {"mes"},
    "Prioridad": {"prioridad"},
    "Categoría": {"categoria"},
    "Tipo": {"tipo"},
    "Solicitado Por": {"solicitado por", "solicitante"},
    "Tiempo Estimado": {
        "tiempo estimado", "tiempo estimado segun prioridad", "tiempo estimado segun",
        "tiempo estimado prioridad"
    },
    "Fecha Inicio": {"fecha inicio", "fecha de inicio", "inicio"},
    "Fecha Terminación": {"fecha terminacion", "fecha de terminacion", "terminacion"},
    "Mes Terminación": {"mes terminacion"},
    "Ejecutado SLA": {"ejecutado segun sla", "ejecutado sla", "cumple sla", "sla"},
    "Tiempo Vs Solicitado": {"tiempo terminado vs solicitado", "tiempo vs solicitado"},
    "Días desde Solicitud": {"dias desde solicitado", "dias desde solicitud"},
    "Estado": {"estado", "status"},
    "Ejecutor": {"ejecutor", "responsable", "tecnico", "tecnico asignado"},
    "Presupuesto": {"presupuesto", "costo presupuesto", "coste"},
    "Materiales": {"materiales"},
    "Link de Soporte": {"link de soporte", "enlace soporte", "url soporte", "evidencia link"},
    "Foto": {"foto", "imagen", "evidencia foto", "image", "picture"}
}

def build_mapping(original_cols):
    """Devuelve dict original->canonico + lista ordenada final respetando PREFERRED_ORDER.
       Usa coincidencia exacta normalizada o 'contains' para robustez."""
    norm_map = {c: _normalize_header(c) for c in original_cols}
    used = set()
    mapping = {}

    # 1) intentar mapear por sinonimos en orden preferido
    for canon in PREFERRED_ORDER:
        targets = SYNONYMS.get(canon, set())
        # primero exact match del normalizado
        found = None
        for c in original_cols:
            if c in used: 
                continue
            n = norm_map[c]
            if n in targets:
                found = c
                break
        # si no, buscar contains
        if not found:
            for c in original_cols:
                if c in used:
                    continue
                n = norm_map[c]
                if any(t in n for t in targets if t):
                    found = c
                    break
        if found:
            mapping[found] = canon
            used.add(found)

    # 2) columnas no mapeadas: conservar su nombre original
    for c in original_cols:
        if c not in mapping:
            mapping[c] = c

    # 3) ordenar: primero los canónicos en el orden preferido,
    #             luego el resto en el orden original
    mapped_names = [mapping[c] for c in original_cols]
    canon_present = [cn for cn in PREFERRED_ORDER if cn in mapped_names]
    others = [name for name in mapped_names if name not in canon_present]

    # Estado al final siempre (si está)
    if "Estado" in canon_present:
        canon_present = [x for x in canon_present if x != "Estado"] + ["Estado"]

    final_order = canon_present + others
    return mapping, final_order
# -----------------------------------------------------------------------------

@st.cache_data(ttl=60)
def cargar_csv(url: str) -> pd.DataFrame:
    # Leer CSV y saltar 3 filas
    df = pd.read_csv(url, dtype=str, encoding="utf-8", skiprows=3, on_bad_lines="skip")

    # Quitar columnas totalmente vacías o encabezados 'Unnamed'
    df = df.loc[:, ~df.columns.astype(str).str.match(r"^\s*Unnamed", na=False)]
    df = df.dropna(axis=1, how="all")

    # Limpiar encabezados
    df.columns = [str(c).strip() for c in df.columns]

    # Construir mapeo inteligente y renombrar
    mapping, final_order = build_mapping(list(df.columns))
    df = df.rename(columns=mapping)

    # Reordenar columnas
    df = df.loc[:, [c for c in final_order if c in df.columns]]

    # Ticket como índice; si no existe, usar primera columna como índice
    if "Ticket" in df.columns:
        df = df.set_index("Ticket")
    else:
        first = df.columns[0]
        df = df.set_index(first)
        df.index.name = "Ticket"

    return df

try:
    df = cargar_csv(CSV_URL)
    st.success(f"✅ Cargado: {len(df)} filas × {len(df.columns)} columnas")
    st.caption(f"Última actualización: {datetime.now():%Y-%m-%d %H:%M:%S}")

    # --------- Filtros / búsqueda (incluye índice Ticket) ----------
    st.subheader("🔎 Buscar")
    opciones = ["(todas)", "Ticket (índice)"] + list(df.columns)
    col = st.selectbox("Columna", opciones)
    q = st.text_input("Texto contiene:", "")

    view = df
    if q:
        qn = str(q)
        if col == "(todas)":
            mask_cols = False
            for c in df.columns:
                mask_cols = mask_cols | df[c].astype(str).str.contains(qn, case=False, na=False)
            mask_idx = df.index.astype(str).str.contains(qn, case=False, na=False)
            view = df[mask_cols | mask_idx]
        elif col == "Ticket (índice)":
            view = df[df.index.astype(str).str.contains(qn, case=False, na=False)]
        else:
            view = df[df[col].astype(str).str.contains(qn, case=False, na=False)]

        st.info(f"Coincidencias: {len(view)}")

    # --------- Agregar "N°" y asegurar 'Estado' al final ----------
    view_display = view.copy()
    view_display.insert(0, "N°", range(1, len(view_display) + 1))
    if "Estado" in view_display.columns:
        cols = [c for c in view_display.columns if c != "Estado"] + ["Estado"]
        view_display = view_display[cols]

    st.dataframe(view_display, use_container_width=True, height=600)

    # --------- Descargar filtrado (Ticket como columna) ----------
    st.download_button(
        "⬇️ Descargar CSV filtrado",
        data=view.reset_index().to_csv(index=False).encode("utf-8-sig"),
        file_name="tickets_filtrados.csv",
        mime="text/csv"
    )

    if st.button("🔄 Refrescar ahora"):
        st.cache_data.clear()
        st.rerun()

except Exception as e:
    st.error(f"❌ No se pudo cargar el CSV: {e}")
    st.info("Revisa la URL RAW en GitHub o el formato del archivo.")
