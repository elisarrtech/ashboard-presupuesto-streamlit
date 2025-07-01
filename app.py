
import streamlit as st
import pandas as pd
import plotly.express as px
import io
from pandas import ExcelWriter

st.set_page_config(page_title="Dashboard Presupuesto", layout="wide")
st.title("📊 Dashboard de Presupuesto Anual")

# 📁 Carga de archivo
uploaded_file = st.file_uploader("📁 Cargar archivo CSV", type=["csv"])

# Si no se carga archivo, se detiene
if uploaded_file is None:
    st.warning("🔄 Por favor carga un archivo CSV para iniciar.")
    st.stop()

# Cargar los datos desde el archivo
df = pd.read_csv(uploaded_file)

# Validar columnas mínimas necesarias
columnas_requeridas = {"Año", "Categoría", "Subcategoría", "Monto", "Aplica IVA"}
if not columnas_requeridas.issubset(df.columns):
    st.error("❌ El archivo no tiene las columnas requeridas.")
    st.stop()

# Calcular IVA y total si no vienen
if "IVA" not in df.columns:
    df["IVA"] = df.apply(lambda row: row["Monto"] * 0.16 if row["Aplica IVA"] == "Sí" else 0, axis=1)

if "Total c/IVA" not in df.columns:
    df["Total c/IVA"] = df["Monto"] + df["IVA"]

# Filtros
with st.sidebar:
    st.header("🔍 Filtros")
    year = st.selectbox("Año", sorted(df["Año"].unique()))
    categoria = st.multiselect("Categoría", df["Categoría"].unique(), default=df["Categoría"].unique())

filtered_df = df[(df["Año"] == year) & (df["Categoría"].isin(categoria))]

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("💼 Total Presupuesto", f"${filtered_df['Monto'].sum():,.2f}")
col2.metric("🧾 Total IVA", f"${filtered_df['IVA'].sum():,.2f}")
col3.metric("📊 Total con IVA", f"${filtered_df['Total c/IVA'].sum():,.2f}")

# Gráfico 1
st.subheader("📈 Distribución por Subcategoría")
fig1 = px.pie(filtered_df, names="Subcategoría", values="Total c/IVA", title="Total con IVA por Subcategoría")
st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2
st.subheader("📊 Comparativa por Categoría")
fig2 = px.bar(filtered_df, x="Categoría", y="Total c/IVA", color="Categoría", title="Totales con IVA por Categoría")
st.plotly_chart(fig2, use_container_width=True)

# Botón para exportar a Excel
buffer = io.BytesIO()
with ExcelWriter(buffer, engine='xlsxwriter') as writer:
    filtered_df.to_excel(writer, index=False, sheet_name="Presupuesto")
    writer.close()

st.download_button(
    label="⬇ Descargar presupuesto filtrado en Excel",
    data=buffer.getvalue(),
    file_name="presupuesto_filtrado.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
