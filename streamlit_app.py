import streamlit as st
import pandas as pd

# ------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ------------------------------
st.set_page_config(page_title="Conciliación NAV vs BANCO", layout="centered")

st.title("📊 Conciliador Automático NAV vs BANCO")
st.write("Sube tus archivos para realizar la conciliación por montos.")

# ------------------------------
# SUBIDA DE ARCHIVOS
# ------------------------------
nav_file = st.file_uploader("📤 Cargar archivo NAV", type=["xlsx", "xls"])
banco_file = st.file_uploader("📤 Cargar archivo BANCO", type=["xlsx", "xls"])

# ------------------------------
# LÓGICA CUANDO SE SUBEN AMBOS ARCHIVOS
# ------------------------------
if nav_file and banco_file:

    # Leer los archivos Excel
    nav = pd.read_excel(nav_file)
    banco = pd.read_excel(banco_file)

    st.success("Archivos cargados correctamente ✅")

    st.subheader("📘 Vista previa NAV")
    st.dataframe(nav.head())

    st.subheader("🏦 Vista previa BANCO")
    st.dataframe(banco.head())

    # Selección de columnas para match
    st.subheader("🧩 Selecciona la columnas requeridas  en cada archivo")

    col_nav = st.selectbox("Columna de monto en NAV", nav.columns)
    col_banco = st.selectbox("Columna de monto en BANCO", banco.columns)

    if st.button("🔍 Realizar Match por Montos"):

        # Convertir columnas a número
        nav[col_nav] = pd.to_numeric(nav[col_nav], errors="coerce")
        banco[col_banco] = pd.to_numeric(banco[col_banco], errors="coerce")

        # ----------------------------------------
        # 1️⃣ MATCH POR MONTOS
        # ----------------------------------------
        match = nav.merge(
            banco,
            left_on=col_nav,
            right_on=col_banco,
            how="inner",
            suffixes=("_NAV", "_BANCO")
        )
        match["Estado"] = "MATCH"

        # ----------------------------------------
        # 2️⃣ NO CONCILIADOS EN NAV
        # ----------------------------------------
        no_nav = nav[~nav[col_nav].isin(banco[col_banco])]
        no_nav["Estado"] = "NO CONCILIADO (NAV)"

        # ----------------------------------------
        # 3️⃣ NO CONCILIADOS EN BANCO
        # ----------------------------------------
        no_banco = banco[~banco[col_banco].isin(nav[col_nav])]
        no_banco["Estado"] = "NO CONCILIADO (BANCO)"

        # ----------------------------------------
        # UNIR TODO EN UN SOLO ARCHIVO
        # ----------------------------------------
        resultado_final = pd.concat([match, no_nav, no_banco], ignore_index=True)

        st.subheader("📄 Resultado Completo")
        st.dataframe(resultado_final)

        # Descargar Excel
        output = pd.ExcelWriter("resultado_conciliacion.xlsx", engine='xlsxwriter')
        resultado_final.to_excel(output, index=False, sheet_name="Resultado")
        output.save()

        with open("resultado_conciliacion.xlsx", "rb") as f:
            st.download_button(
                label="📥 Descargar archivo conciliado",
                data=f,
                file_name="conciliacion_NAV_vs_BANCO.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        st.success("Conciliación realizada con éxito 🎉")


