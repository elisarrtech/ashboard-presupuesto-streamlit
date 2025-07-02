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
    df = pd.read_csv("presupuesto_consolidado.csv", parse_dates=["Fecha de Pago"])
    return df

df = load_data()

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
meses = df["Mes"].unique()
bancos = df["Banco"].unique()

colf1, colf2 = st.columns(2)
mes_sel = colf1.multiselect("📅 Filtrar por mes", opciones := sorted(meses), default=meses)
banco_sel = colf2.multiselect("🏦 Filtrar por banco", opciones := sorted(bancos), default=bancos)

# Aplicar filtros
df_filtrado = df[df["Mes"].isin(mes_sel) & df["Banco"].isin(banco_sel)]

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

# Gráfico: Gasto por banco
st.subheader("🏦 Gasto por banco")
gasto_banco = df_filtrado.groupby("Banco")["Monto"].sum().reset_index().sort_values("Monto", ascending=False)
chart_banco = alt.Chart(gasto_banco).mark_bar().encode(
    x="Monto",
    y=alt.Y("Banco", sort="-x"),
    tooltip=["Banco", "Monto"]
)
st.altair_chart(chart_banco, use_container_width=True)

# Tabla de datos
st.subheader("📄 Detalle de gastos filtrados")
st.dataframe(df_filtrado.sort_values("Fecha de Pago"))
