# components/visuals.py
import streamlit as st
import plotly.express as px
import plotly.io as pio
from calendar import month_name
from datetime import datetime
import pandas as pd

# Diccionario de meses en español
meses_es = {i: month_name[i] for i in range(1, 13)}

def show_kpis(df):
    col1, col2, col3 = st.columns(3)

    total = df['Monto'].sum()
    pagado = df[df['Status'].str.upper() == 'PAGADO']['Monto'].sum()
    no_pagado = df[df['Status'].str.upper() != 'PAGADO']['Monto'].sum()

    col1.metric("💰 Total Gastado", f"${total:,.0f}")
    col2.metric("✅ Pagado", f"${pagado:,.0f}")
    col3.metric("⚠️ Por Pagar", f"${no_pagado:,.0f}")
    st.divider()

def plot_gasto_por_mes(df):
    st.subheader("📈 Gasto total por mes")
    df['Mes_num'] = df['Fecha'].dt.month
    gasto_mes = df.groupby("Mes_num")["Monto"].sum().reset_index()
    gasto_mes['Mes'] = gasto_mes['Mes_num'].apply(lambda x: meses_es.get(x, ""))
    gasto_mes = gasto_mes.sort_values("Mes_num")

    fig = px.bar(gasto_mes, x="Mes", y="Monto", text_auto=True,
                 title="Gasto total por mes", labels={"Monto": "Monto Total", "Mes": "Mes"})
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside")
    
    if st.button("💾 Descargar gráfico como PNG"):
        pio.write_image(fig, "gasto_por_mes.png")
        with open("gasto_por_mes.png", "rb") as file:
            st.download_button(label="⬇️ Confirmar descarga", data=file, file_name="gasto_por_mes.png", mime="image/png")
    
    st.plotly_chart(fig, use_container_width=True)

def plot_gasto_por_categoria(df):
    st.subheader("🏦 Gasto por categoría")
    gasto_cat = df.groupby("Categoría")["Monto"].sum().reset_index().sort_values("Monto", ascending=False)

    fig = px.bar(gasto_cat, x="Monto", y="Categoría", orientation='h', text_auto=True,
                 title="Gasto total por categoría", labels={"Monto": "Monto Total", "Categoría": "Categoría"})
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

def show_filtered_table(df):
    st.subheader("📄 Detalle de gastos filtrados")
    st.dataframe(df.sort_values("Fecha"))

def show_month_comparison(df):
    df["Mes_num"] = df["Fecha"].dt.month
    monthly_spending = df.groupby("Mes_num")["Monto"].sum().reset_index()

    current_month = datetime.today().month
    last_month = current_month - 1 if current_month > 1 else 12

    current_total = monthly_spending.loc[monthly_spending["Mes_num"] == current_month, "Monto"].sum()
    last_total = monthly_spending.loc[monthly_spending["Mes_num"] == last_month, "Monto"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("📅 Mes actual", meses_es[current_month])
    col2.metric("💰 Gasto mes actual", f"${current_total:,.0f}", delta=f"{current_total - last_total:,.0f} vs. mes anterior")
    col3.metric("📅 Mes anterior", meses_es[last_month])

def show_categoria_presupuesto(df, presupuesto_categoria={}):
    st.subheader("🎯 Comparación: Gasto vs. Presupuesto por Categoría")

    gasto_cat = df.groupby("Categoría")["Monto"].sum().reset_index()

    data = []
    for cat in gasto_cat["Categoría"].unique():
        presupuesto = presupuesto_categoria.get(cat, 0.0)
        gasto = gasto_cat.loc[gasto_cat["Categoría"] == cat, "Monto"].sum()

        data.append({
            "Categoría": cat,
            "Presupuesto": float(presupuesto),
            "Gasto Real": float(gasto),
            "Diferencia": float(gasto - presupuesto)
        })

    if not data:
        st.warning("⚠️ No hay categorías coincidentes entre tus datos y el presupuesto definido.")
        return pd.DataFrame(columns=["Categoría", "Presupuesto", "Gasto Real", "Diferencia"])

    df_presupuesto = pd.DataFrame(data)

    # Mostrar tabla con diferencias resaltadas
    st.dataframe(df_presupuesto.style.applymap(
        lambda val: "background-color:red; color:white" if val > 0 else "",
        subset=["Diferencia"]
    ))

    return df_presupuesto
