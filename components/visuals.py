# components/visuals.py
import streamlit as st
import altair as alt

def show_kpis(df):
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Gastado", f"${df['Monto'].sum():,.0f}")
    col2.metric("✅ Pagado", f"${df[df['Status'] == 'PAGADO']['Monto'].sum():,.0f}")
    col3.metric("⚠️ Por Pagar", f"${df[df['Status'] != 'PAGADO']['Monto'].sum():,.0f}")
    st.divider()

import plotly.express as px

def plot_gasto_por_mes(df_filtrado):
    st.subheader("📈 Gasto total por mes")
    gasto_mes = df_filtrado.groupby("Mes")["Monto"].sum().reset_index()
    gasto_mes = gasto_mes.sort_values("Mes")

    fig = px.bar(gasto_mes, x="Mes", y="Monto", text_auto=True,
                 title="Gasto total por mes", labels={"Monto": "Monto Total", "Mes": "Mes"})
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

def plot_gasto_por_categoria(df_filtrado):
    st.subheader("🏦 Gasto por categoría")
    gasto_cat = df_filtrado.groupby("Categoría")["Monto"].sum().reset_index().sort_values("Monto", ascending=False)

    fig = px.bar(gasto_cat, x="Monto", y="Categoría", orientation='h', text_auto=True,
                 title="Gasto total por categoría", labels={"Monto": "Monto Total", "Categoría": "Categoría"})
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

def show_filtered_table(df_filtrado):
    st.subheader("📄 Detalle de gastos filtrados")
    st.dataframe(df_filtrado.sort_values("Fecha"))
