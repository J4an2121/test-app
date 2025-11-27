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

    # Leer archivos
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

    # Botón ejecutar
    if st.button("🔍 Realizar Match por Montos"):

        # Convertir columnas a numérico
        nav[col_nav] = pd.to_numeric(nav[col_nav], errors="coerce")
        banco[col_banco] = pd.to_numeric(banco[col_banco], errors="coerce")

        # DataFrames simplificados
        nav2 = nav[[col_nav]].rename(columns={col_nav: "NAV_monto"})
        banco2 = banco[[col_banco]].rename(columns={col_banco: "BANCO_monto"})

        # FULL OUTER JOIN → trae matches y no matches
        resultado = nav2.merge(
            banco2,
            left_on="NAV_monto",
            right_on="BANCO_monto",
            how="outer"
        )

        # Columna MATCH / NO MATCH
        resultado["MATCH"] = resultado.apply(
            lambda x: "✅ MATCH" if pd.notnull(x["NAV_monto"]) and pd.notnull(x["BANCO_monto"]) else "❌ NO MATCH",
            axis=1
        )

        # Mostrar tabla
        st.subheader("📄 Resultado del Match (columnas independientes)")
        st.dataframe(resultado)

        # ------------------------------
        # CREAR ARCHIVO EXCEL EN MEMORIA
        # ------------------------------
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            resultado.to_excel(writer, index=False, sheet_name="Conciliacion")

        # Botón descargar
        st.download_button(
            label="📥 Descargar resultado en Excel",
            data=output.getvalue(),
            file_name="conciliacion_NAV_vs_BANCO.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.success("Conciliación completada con MATCH / NO MATCH 🎉")




