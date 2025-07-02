import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# Título y configuración
st.set_page_config(page_title="Dashboard de Presupuesto", layout="wide")
st.title("📊 Dashboard de Presupuesto de Gastos")

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv("presupuesto_consolidado_v2.csv", parse_dates=["Fecha"])
    return df

df = load_data()

# Validar columnas requeridas
required_columns = ["Fecha", "Categoría", "Concepto", "Monto", "Status"]
if not all(col in df.columns for col in required_columns):
    st.error("❌ El archivo no tiene las columnas requeridas.")
    st.stop()

# KPIs
col1, col2, col3 = st.columns(3)
total_gastado = df["Monto"].sum()
pagado = df[df["Status"] == "PAGADO"]["Monto"].sum()
por_pagar = df[df["Status"] != "PAGADO"]["Monto"].sum()

col1.metric("💰 Total Gastado", f"${total_gastado:,.0f}")
col2.metric("✅ Pagado", f"${pagado:,.0f}")
col3.metric("⚠️ Por Pagar", f"${por_pagar:,.0f}")

st.divider()

# Filtros
meses = df["Fecha"].dt.strftime("%B").unique()
categorias = df["Categoría"].unique()

colf1, colf2 = st.columns(2)
mes_sel = colf1.multiselect("📅 Filtrar por mes", opciones := sorted(meses), default=meses)
banco_sel = colf2.multiselect("🏦 Filtrar por categoría", opciones := sorted(categorias), default=categorias)

# Aplicar filtros
df["Mes"] = df["Fecha"].dt.strftime("%B")
df_filtrado = df[df["Mes"].isin(mes_sel) & df["Categoría"].isin(banco_sel)]

# Alertas
pendientes = df_filtrado[df_filtrado["Status"] != "PAGADO"]
if not pendientes.empty:
    st.warning(f"🔔 Hay {len(pendientes)} conceptos pendientes de pago")
    with st.expander("Ver pendientes"):
        st.dataframe(pendientes)

# Gráfico: Gasto por mes
st.subheader("📈 Gasto total por mes")
gasto_mes = df_filtrado.groupby("Mes")["Monto"].sum().reset_index()
chart_mes = alt.Chart(gasto_mes).mark_bar().encode(
    x=alt.X("Mes", sort=list(sorted(df["Mes"].unique()))),
    y="Monto",
    tooltip=["Mes", "Monto"]
)
st.altair_chart(chart_mes, use_container_width=True)

# Gráfico: Gasto por categoría
st.subheader("🏦 Gasto por categoría")
gasto_banco = df_filtrado.groupby("Categoría")["Monto"].sum().reset_index().sort_values("Monto", ascending=False)
chart_banco = alt.Chart(gasto_banco).mark_bar().encode(
    x="Monto",
    y=alt.Y("Categoría", sort="-x"),
    tooltip=["Categoría", "Monto"]
)
st.altair_chart(chart_banco, use_container_width=True)

# Tabla de datos
st.subheader("📄 Detalle de gastos filtrados")
st.dataframe(df_filtrado.sort_values("Fecha"))
