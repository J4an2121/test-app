import streamlit as st
import pandas as pd
import io
import numpy as np

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

    st.subheader("🧩 Selecciona la columna ")

    col_nav = st.selectbox("Columna de en NAV", nav.columns)
    col_banco = st.selectbox("Columna de  en BANCO", banco.columns)

    if st.button("🔍 Realizar Match por Montos"):

        # Convertir a número
        nav[col_nav] = pd.to_numeric(nav[col_nav], errors="coerce")
        banco[col_banco] = pd.to_numeric(banco[col_banco], errors="coerce")

        # Listas de valores
        nav_list = nav[col_nav].dropna().tolist()
        banco_list = banco[col_banco].dropna().tolist()

        # Hacer que tengan la misma longitud
        max_len = max(len(nav_list), len(banco_list))
        nav_list.extend([np.nan] * (max_len - len(nav_list)))
        banco_list.extend([np.nan] * (max_len - len(banco_list)))

        # Crear DataFrame alineado
        resultado = pd.DataFrame({
            "NAV_monto": nav_list,
            "BANCO_monto": banco_list
        })

        # Columna MATCH / NO MATCH
        resultado["MATCH"] = resultado.apply(
            lambda row: "✅ MATCH" if row["NAV_monto"] == row["BANCO_monto"] else "❌ NO MATCH",
            axis=1
        )

        st.subheader("📄 Resultado del Match (lado a lado)")
        st.dataframe(resultado)

        # Crear Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            resultado.to_excel(writer, index=False, sheet_name="Conciliacion")

        # Descarga
        st.download_button(
            label="📥 Descargar resultado en Excel",
            data=output.getvalue(),
            file_name="conciliacion_NAV_vs_BANCO.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.success("Conciliación realizada 🎉")
