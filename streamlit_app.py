
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

            # Limpiar nulos y renombrar
            nav_clean = nav.dropna(subset=[col_nav]).copy()
            banco_clean = banco.dropna(subset=[col_banco]).copy()

            nav_clean.rename(columns={col_nav: "Monto"}, inplace=True)
            banco_clean.rename(columns={col_banco: "Monto"}, inplace=True)

            # Crear índice para manejar duplicados
            nav_clean["idx"] = nav_clean.groupby("Monto").cumcount()
            banco_clean["idx"] = banco_clean.groupby("Monto").cumcount()

            # Merge para emparejar ocurrencias
            conciliado = pd.merge(
                nav_clean, banco_clean,
                on=["Monto", "idx"], how="outer", indicator=True,
                suffixes=("_NAV", "_BANCO")
            )

            # Estado MATCH / NO MATCH
            conciliado["Estado"] = conciliado["_merge"].map({
                "both": "✅ MATCH",
                "left_only": "❌ NO MATCH (solo NAV)",
                "right_only": "❌ NO MATCH (solo BANCO)"
            })

            # Mostrar resultado completo
            st.subheader("📄 Resultado del Match (detalle)")
            st.dataframe(conciliado[["Monto", "Estado", "Document No._NAV", "Document No._BANCO"]])

            # Separar no coincidencias
            nav_unmatched = conciliado[conciliado["Estado"] == "❌ NO MATCH (solo NAV)"]
            banco_unmatched = conciliado[conciliado["Estado"] == "❌ NO MATCH (solo BANCO)"]

            # Exportar a Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                conciliado.to_excel(writer, index=False, sheet_name="Conciliacion")
                nav_unmatched.to_excel(writer, index=False, sheet_name="NAV sin match")
                banco_unmatched.to_excel(writer, index=False, sheet_name="BANCO sin match")

            st.download_button(
                label="📥 Descargar resultado en Excel",
                data=output.getvalue(),
                file_name="conciliacion_NAV_vs_BANCO.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

