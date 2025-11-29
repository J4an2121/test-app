
import streamlit as st
import pandas as pd
import io
from decimal import Decimal, ROUND_HALF_UP

# ------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ------------------------------
st.set_page_config(page_title="Conciliación NAV vs BANCO", layout="centered")

# ==============================
# AUTH BÁSICA (DEMO)
# ==============================
USUARIO = "admin"
CLAVE = "1234"

# Inicializa estado de sesión
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

def login_view():
    st.title("🔒 Acceso | Conciliación NAV vs BANCO")
    usuario = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if usuario == USUARIO and clave == CLAVE:
            st.session_state.autenticado = True
            st.experimental_rerun()
        else:
            st.error("Credenciales incorrectas ❌")

def logout_button():
    st.sidebar.button("Cerrar sesión", on_click=lambda: st.session_state.update({"autenticado": False}))
    # Puedes limpiar variables sensibles aquí si las usas

# Si NO autenticado → mostrar login y salir
if not st.session_state.autenticado:
    login_view()
    st.stop()

# Si SÍ autenticado → mostrar la app
logout_button()
st.title("📊 Conciliador Automático NAV vs BANCO")
st.write("Sube tus archivos para realizar la conciliación por montos (MATCH / NO MATCH).")

# ------------------------------
# SUBIDA DE ARCHIVOS
# ------------------------------
nav_file = st.file_uploader("📤 Cargar archivo NAV", type=["xlsx", "xls"])
banco_file = st.file_uploader("📤 Cargar archivo BANCO", type=["xlsx", "xls"])

# ------------------------------
# FUNCIONES AUXILIARES
# ------------------------------
def to_decimal_normalized(x):
    if pd.isna(x):
        return None
    try:
        s = str(x).strip()
        for ch in [",", " ", "$"]:
            s = s.replace(ch, "")
        if s.startswith("(") and s.endswith(")"):
            s = "-" + s[1:-1]
        val = Decimal(s)
        return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except Exception:
        try:
            val = Decimal(float(x))
            return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except Exception:
            return None

def normalize_amount_column(df, col_name, new_name="Monto"):
    tmp = df.copy()
    tmp[new_name] = tmp[col_name].apply(to_decimal_normalized)
    tmp = tmp.dropna(subset=[new_name])
    return tmp

# ------------------------------
# LÓGICA CUANDO SE SUBEN AMBOS ARCHIVOS
# ------------------------------
if nav_file and banco_file:
    nav = pd.read_excel(nav_file)
    banco = pd.read_excel(banco_file)

    st.success("Archivos cargados correctamente ✅")

    st.subheader("📘 Vista previa NAV")
    st.dataframe(nav.head(10))

    st.subheader("🏦 Vista previa BANCO")
    st.dataframe(banco.head(10))

    st.subheader("🧩 Selecciona la columna de montos")
    col_nav = st.selectbox("Columna de monto en NAV", nav.columns, key="col_nav")
    col_banco = st.selectbox("Columna de monto en BANCO", banco.columns, key="col_banco")

    st.subheader("📎 (Opcional) Selecciona columnas de referencia para mostrar")
    ref_nav = st.multiselect("Columnas de referencia NAV", nav.columns, default=[c for c in ["Document No.", "Posting Date", "Description"] if c in nav.columns])
    ref_banco = st.multiselect("Columnas de referencia BANCO", banco.columns, default=[c for c in ["Document No.", "Posting Date", "Description"] if c in banco.columns])

    ver_solo_match = st.checkbox("👀 Mostrar solo los registros que hacen MATCH", value=True)

    if st.button("🔍 Realizar Match por Montos", type="primary"):
        with st.spinner("Realizando conciliación..."):
            nav_norm = normalize_amount_column(nav, col_nav, "Monto")
            banco_norm = normalize_amount_column(banco, col_banco, "Monto")

            nav_nulos = nav[col_nav].isna().sum()
            banco_nulos = banco[col_banco].isna().sum()
            if nav_nulos > 0:
                st.warning(f"NAV: {nav_nulos} valores nulos en '{col_nav}' (se excluyen).")
            if banco_nulos > 0:
                st.warning(f"BANCO: {banco_nulos} valores nulos en '{col_banco}' (se excluyen).")

            nav_norm["idx"] = nav_norm.groupby("Monto").cumcount()
            banco_norm["idx"] = banco_norm.groupby("Monto").cumcount()

            nav_show = nav_norm[[*ref_nav, "Monto", "idx"]] if ref_nav else nav_norm[["Monto", "idx"]]
            banco_show = banco_norm[[*ref_banco, "Monto", "idx"]] if ref_banco else banco_norm[["Monto", "idx"]]

            nav_show = nav_show.rename(columns={c: f"{c}_NAV" for c in ref_nav})
            banco_show = banco_show.rename(columns={c: f"{c}_BANCO" for c in ref_banco})

            merged = pd.merge(nav_show, banco_show, on=["Monto", "idx"], how="outer", indicator=True)

            merged["Estado"] = merged["_merge"].map({
                "both": "✅ MATCH",
                "left_only": "❌ NO MATCH (solo NAV)",
                "right_only": "❌ NO MATCH (solo BANCO)"
            })

            view_df = merged[merged["Estado"] == "✅ MATCH"].copy() if ver_solo_match else merged.copy()
            view_df = view_df.sort_values(by=["Estado", "Monto", "idx"], ascending=[True, True, True])

            st.subheader("📄 Resultado del Match (detalle)")
            st.dataframe(view_df)

            match_df = merged[merged["Estado"] == "✅ MATCH"].sort_values(["Monto", "idx"])
            nav_unmatched_df = merged[merged["Estado"] == "❌ NO MATCH (solo NAV)"].sort_values(["Monto", "idx"])
            banco_unmatched_df = merged[merged["Estado"] == "❌ NO MATCH (solo BANCO)"].sort_values(["Monto", "idx"])

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                match_df.to_excel(writer, index=False, sheet_name="MATCH (detalle)")
                nav_unmatched_df.to_excel(writer, index=False, sheet_name="NAV sin match")
                banco_unmatched_df.to_excel(writer, index=False, sheet_name="BANCO sin match")

            st.download_button(
                label="📥 Descargar conciliación en Excel",
                data=output.getvalue(),
                file_name="conciliacion_NAV_vs_BANCO.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            total_matches = len(match_df)
            total_nav_only = len(nav_unmatched_df)
            total_banco_only = len(banco_unmatched_df)
            c1, c2, c3 = st.columns(3)
            c1.metric("Emparejamientos (MATCH)", total_matches)
            c2.metric("Sin match (NAV)", total_nav_only)
            c3.metric("Sin match (BANCO)", total_banco_only)

