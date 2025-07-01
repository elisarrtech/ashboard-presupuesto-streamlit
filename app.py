
import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar datos
df = pd.read_csv("presupuesto_demo.csv")

st.set_page_config(page_title="Dashboard Presupuesto", layout="wide")
st.title("📊 Dashboard de Presupuesto Anual")

# Filtros
with st.sidebar:
    st.header("🔍 Filtros")
    year = st.selectbox("Año", sorted(df["Año"].unique()), index=0)
    categoria = st.multiselect("Categoría", df["Categoría"].unique(), default=df["Categoría"].unique())

# Filtrar datos
filtered_df = df[(df["Año"] == year) & (df["Categoría"].isin(categoria))]

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("💼 Total Presupuesto", f"${filtered_df['Monto'].sum():,.2f}")
col2.metric("🧾 Total IVA", f"${filtered_df['IVA'].sum():,.2f}")
col3.metric("📊 Total con IVA", f"${filtered_df['Total c/IVA'].sum():,.2f}")

# Gráficos
st.subheader("📈 Distribución por Subcategoría")
fig_pie = px.pie(filtered_df, names="Subcategoría", values="Total c/IVA", title="Total con IVA por Subcategoría")
st.plotly_chart(fig_pie, use_container_width=True)

st.subheader("📊 Comparativa por Categoría")
fig_bar = px.bar(filtered_df, x="Categoría", y="Total c/IVA", color="Categoría", title="Totales con IVA por Categoría")
st.plotly_chart(fig_bar, use_container_width=True)
