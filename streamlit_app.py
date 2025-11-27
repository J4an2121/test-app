import streamlit as st
import pandas as pd
import io

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

    nav = pd.read_excel(nav_file)
    banco = pd.read_excel(banco_file)

    st.success("Archivos cargados correctamente ✅")

    st.subheader("📘 Vista previa NAV")
    st.dataframe(nav.head())

    st.subheader("🏦 Vista previa BANCO")
    st.dataframe(banco.head())

    st.subheader("🧩 Selecciona las columnas requeridas")

    col_nav = st.selectbox("Columna de monto en NAV", nav.columns)
    col_banco = st.selectbox("Columna de monto en BANCO", banco.columns)

    if st.button("🔍 Realizar Match por Montos"):

        # Convertir columnas a número
        nav[col_nav] = pd.to_numeric(nav[col_nav], errors="coerce")
        banco[col_banco] = pd.to_numeric(banco[col_banco], errors="coerce")

        # Match por montos
        resultado = nav.merge(
            banco,
            left_on=col_nav,
            right_on=col_banco,
            how="inner",
            suffixes=("_NAV", "_BANCO")
        )

        st.subheader("📄 Resultado del Match")
        st.dataframe(resultado)

        # ------------------------------
        # CREAR EXCEL EN MEMORIA
        # ------------------------------
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            resultado.to_excel(writer, index=False, sheet_name="Conciliacion")

        # Descargar
        st.download_button(
            label="📥 Descargar resultado en Excel",
            data=output.getvalue(),
            file_name="conciliacion_NAV_vs_BANCO.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.success("Conciliación finalizada 🎉")


