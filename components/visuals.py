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
import plotly.io as pio

def plot_gasto_por_mes(df_filtrado):
    st.subheader("📈 Gasto total por mes")
    gasto_mes = df_filtrado.groupby("Mes")["Monto"].sum().reset_index()
    gasto_mes = gasto_mes.sort_values("Mes")

    fig = px.bar(gasto_mes, x="Mes", y="Monto", text_auto=True,
                 title="Gasto total por mes", labels={"Monto": "Monto Total", "Mes": "Mes"})
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside")
    
    # Botón de descarga
    if st.button("💾 Descargar gráfico como PNG"):
        pio.write_image(fig, "gasto_por_mes.png")
        with open("gasto_por_mes.png", "rb") as file:
            btn = st.download_button(label="⬇️ Confirmar descarga", data=file, file_name="gasto_por_mes.png", mime="image/png")
    
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

def show_month_comparison(df):
    df["Mes_num"] = df["Fecha"].dt.month
    monthly_spending = df.groupby("Mes_num")["Monto"].sum().reset_index()

    current_month = datetime.today().month
    last_month = current_month - 1 if current_month > 1 else 12

    current_total = monthly_spending[monthly_spending["Mes_num"] == current_month]["Monto"].sum()
    last_total = monthly_spending[monthly_spending["Mes_num"] == last_month]["Monto"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("📅 Mes actual", meses_es[current_month], delta="")
    col2.metric("💰 Gasto mes actual", f"${current_total:,.0f}", delta=f"{current_total - last_total:,.0f} vs. mes anterior")
    col3.metric("📅 Mes anterior", meses_es[last_month], delta="")

def show_categoria_presupuesto(df, presupuesto_categoria):
    st.subheader("🎯 Comparación: Gasto vs. Presupuesto por Categoría")

    gasto_cat = df.groupby("Categoría")["Monto"].sum().reset_index()
    data = []

    for cat, presupuesto in presupuesto_categoria.items():
        gasto = gasto_cat[gasto_cat["Categoría"] == cat]["Monto"].sum()
        data.append({
            "Categoría": cat,
            "Presupuesto": presupuesto,
            "Gasto Real": gasto,
            "Diferencia": gasto - presupuesto
        })

    df_presupuesto = pd.DataFrame(data)

    # Mostrar tabla comparativa
    st.dataframe(df_presupuesto.style.applymap(
        lambda x: "background-color:red; color:white" if x > 0 and "Diferencia" in str(x) else "",
        subset=["Diferencia"]
    ))

    return df_presupuesto
