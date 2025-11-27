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
    st.subheader("🧩 Selecciona la columna de monto en cada archivo")

    col_nav = st.selectbox("Columna de monto en NAV", nav.columns)
    col_banco = st.selectbox("Columna de monto en BANCO", banco.columns)

    if st.button("🔍 Realizar Match por Montos"):

        # Convertir todo a numérico por seguridad
        nav[col_nav] = pd.to_numeric(nav[col_nav], errors="coerce")
        banco[col_banco] = pd.to_numeric(banco[col_banco], errors="coerce")

        # Hacer match por montos
        resultado = nav.merge(
            banco,
            left_on=col_nav,
            right_on=col_banco,
            how="inner",
            suffixes=("_NAV", "_BANCO")
        )

        st.subheader("📄 Resultado del Match")
        st.dataframe(resultado)

        # Descargar Excel
        output = pd.ExcelWriter("resultado_conciliacion.xlsx", engine='xlsxwriter')
        resultado.to_excel(output, index=False, sheet_name="Conciliacion")
        output.save()

        with open("resultado_conciliacion.xlsx", "rb") as f:
            st.download_button(
                label="📥 Descargar resultado en Excel",
                data=f,
                file_name="conciliacion_NAV_vs_BANCO.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        st.success("Conciliación realizada y archivo listo para descargar 🎉")
