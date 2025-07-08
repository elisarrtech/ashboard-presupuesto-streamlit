import streamlit as st
import plotly.express as px
from calendar import month_name
from datetime import datetime
import pandas as pd

meses_es = {i: month_name[i] for i in range(1, 13)}

def show_kpis(df, topes_mensuales, filtro_mes=None):
    if filtro_mes:
        df = df[df['Mes_num'].isin(filtro_mes)]

    total_gastado = df['Monto'].sum()
    pagado = df[df['Status'].str.upper() == 'PAGADO']['Monto'].sum()
    pendiente = df[df['Status'].str.upper() != 'PAGADO']['Monto'].sum()

    current_month = datetime.today().month
    gasto_mes_actual = df[df['Mes_num'] == current_month]['Monto'].sum()
    tope_mes = topes_mensuales.get(current_month, 0)
    diferencia_mes = gasto_mes_actual - tope_mes
    cumplimiento = (gasto_mes_actual / tope_mes * 100) if tope_mes else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("💰 Total Gastado", f"${total_gastado:,.0f}")
    col2.metric("📅 Gastado Mes Actual", f"${gasto_mes_actual:,.0f}")
    col3.metric("✅ Pagado", f"${pagado:,.0f}")
    col4.metric("⚠️ Por Pagar", f"${pendiente:,.0f}")
    col5.metric("🎯 Cumplimiento Mes", f"{cumplimiento:.1f}%", delta=f"{diferencia_mes:,.0f}")

def plot_gasto_por_mes(df, filtro_mes=None):
    if filtro_mes:
        df = df[df['Mes_num'].isin(filtro_mes)]

    gasto_mes = df.groupby("Mes_num")["Monto"].sum().reset_index()
    gasto_mes['Mes'] = gasto_mes['Mes_num'].apply(lambda x: meses_es.get(x, ""))

    fig = px.bar(gasto_mes.sort_values("Mes_num"), x="Mes", y="Monto", text_auto=True,
                 title="📊 Gasto total por mes", labels={"Monto": "Monto Total", "Mes": "Mes"})
    st.plotly_chart(fig, use_container_width=True)

def show_monthly_topes(df, topes_mensuales, filtro_mes=None):
    if filtro_mes:
        df = df[df['Mes_num'].isin(filtro_mes)]

    gasto_mes = df.groupby("Mes_num")["Monto"].sum().reset_index()
    gasto_mes['Mes'] = gasto_mes['Mes_num'].apply(lambda x: meses_es.get(x, ""))
    gasto_mes['Tope'] = gasto_mes['Mes_num'].apply(lambda x: topes_mensuales.get(x, 0))

    fig = px.bar(gasto_mes.sort_values("Mes_num"), x="Mes", y=["Monto", "Tope"], barmode='group',
                 title="📊 Comparativo Gasto vs. Tope mensual",
                 labels={"value": "Monto", "Mes": "Mes", "variable": "Concepto"})
    st.plotly_chart(fig, use_container_width=True)

def plot_gasto_por_categoria(df, filtro_mes=None):
    if filtro_mes:
        df = df[df['Mes_num'].isin(filtro_mes)]

    gasto_cat = df.groupby("Categoría")["Monto"].sum().reset_index().sort_values("Monto", ascending=False)

    fig = px.bar(gasto_cat, x="Monto", y="Categoría", orientation='h', text_auto=True,
                 title="🏦 Gasto por categoría", labels={"Monto": "Monto Total", "Categoría": "Categoría"})
    st.plotly_chart(fig, use_container_width=True)

def show_filtered_table(df):
    st.subheader("📄 Detalle de gastos filtrados")
    columnas = [col for col in ["Fecha de pago", "Mes_num", "Mes", "Categoría", "Banco", "Concepto", "Monto", "Status"] if col in df.columns]

    df = df.loc[:, ~df.columns.duplicated()]
    df.columns = [str(col).strip() for col in df.columns]

    st.dataframe(df.sort_values("Fecha de pago")[columnas])

def show_month_comparison(df):
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

    df_presupuesto = pd.DataFrame(data)

    if "Diferencia" in df_presupuesto.columns and not df_presupuesto.empty:
        st.dataframe(df_presupuesto.style.applymap(
            lambda val: "background-color:red; color:white" if isinstance(val, (int, float)) and val > 0 else "",
            subset=["Diferencia"]
        ))
    else:
        st.warning("⚠️ No hay datos para mostrar en la comparación de presupuesto.")

    return df_presupuesto
