# components/visuals.py
import streamlit as st
import altair as alt

def show_kpis(df):
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Gastado", f"${df['Monto'].sum():,.0f}")
    col2.metric("✅ Pagado", f"${df[df['Status'] == 'PAGADO']['Monto'].sum():,.0f}")
    col3.metric("⚠️ Por Pagar", f"${df[df['Status'] != 'PAGADO']['Monto'].sum():,.0f}")
    st.divider()

def plot_gasto_por_mes(df_filtrado):
    st.subheader("📈 Gasto total por mes")
    gasto_mes = df_filtrado.groupby("Mes")["Monto"].sum().reset_index()
    gasto_mes = gasto_mes.sort_values("Mes")
    chart_mes = alt.Chart(gasto_mes).mark_bar().encode(
        x=alt.X("Mes", title="Mes"),
        y=alt.Y("Monto", title="Monto Total"),
        tooltip=["Mes", "Monto"]
    )
    st.altair_chart(chart_mes, use_container_width=True)

def plot_gasto_por_categoria(df_filtrado):
    st.subheader("🏦 Gasto por categoría")
    gasto_cat = df_filtrado.groupby("Categoría")["Monto"].sum().reset_index().sort_values("Monto", ascending=False)
    st.altair_chart(alt.Chart(gasto_cat).mark_bar().encode(
        x="Monto",
        y=alt.Y("Categoría", sort="-x"),
        tooltip=["Categoría", "Monto"]
    ), use_container_width=True)

def show_filtered_table(df_filtrado):
    st.subheader("📄 Detalle de gastos filtrados")
    st.dataframe(df_filtrado.sort_values("Fecha"))
