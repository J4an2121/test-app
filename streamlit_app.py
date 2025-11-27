
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

    st.subheader("🧩 Selecciona la columna de montos")

    col_nav = st.selectbox("Columna de monto en NAV", nav.columns)
    col_banco = st.selectbox("Columna de monto en BANCO", banco.columns)

    if st.button("🔍 Realizar Match por Montos"):

        with st.spinner("Realizando conciliación..."):

            # Convertir a número
            nav[col_nav] = pd.to_numeric(nav[col_nav], errors="coerce")
            banco[col_banco] = pd.to_numeric(banco[col_banco], errors="coerce")

            # Limpiar nulos y renombrar columnas
            nav_clean = nav[[col_nav]].dropna().rename(columns={col_nav: "Monto"})
            banco_clean = banco[[col_banco]].dropna().rename(columns={col_banco: "Monto"})

            # Agregar fuente
            nav_clean["Fuente"] = "NAV"
            banco_clean["Fuente"] = "BANCO"

            # Concatenar para análisis
            todos = pd.concat([nav_clean, banco_clean])

            # Contar ocurrencias y clasificar
            conteo = todos.groupby("Monto")["Fuente"].apply(list).reset_index()
            conteo["MATCH"] = conteo["Fuente"].apply(
                lambda x: "✅ MATCH" if len(set(x)) > 1 else "❌ NO MATCH"
            )

            # Identificar no coincidencias
            nav_unmatched = nav_clean[~nav_clean["Monto"].isin(banco_clean["Monto"])]
            banco_unmatched = banco_clean[~banco_clean["Monto"].isin(nav_clean["Monto"])]

            # Mostrar resultados
            st.subheader("📄 Resultado del Match")
            st.dataframe(conteo)

            st.subheader("Montos en NAV sin match")
            st.dataframe(nav_unmatched)

            st.subheader("Montos en BANCO sin match")
            st.dataframe(banco_unmatched)

            # Exportar a Excel con varias hojas
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                conteo.to_excel(writer, index=False, sheet_name="Conciliacion")
                nav_unmatched.to_excel(writer, index=False, sheet_name="NAV sin match")
                banco_unmatched.to_excel(writer, index=False, sheet_name="BANCO sin match")

            st.download_button(
                label="📥 Descargar resultado en Excel",
                data=output.getvalue(),
                file_name="conciliacion_NAV_vs_BANCO.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.success("Conciliación realizada 🎉")



