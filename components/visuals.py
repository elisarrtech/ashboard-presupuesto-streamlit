# components/visuals.py

import streamlit as st
import plotly.express as px
import plotly.io as pio
from calendar import month_name
from datetime import datetime  # ✅ Importación añadida aquí

meses_es = {i: month_name[i] for i in range(1, 13)}

def show_month_comparison(df):
    df["Mes_num"] = df["Fecha"].dt.month
    monthly_spending = df.groupby("Mes_num")["Monto"].sum().reset_index()

    current_month = datetime.today().month  # ✅ Ahora funciona
    last_month = current_month - 1 if current_month > 1 else 12

    current_total = monthly_spending[monthly_spending["Mes_num"] == current_month]["Monto"].sum()
    last_total = monthly_spending[monthly_spending["Mes_num"] == last_month]["Monto"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("📅 Mes actual", meses_es[current_month], delta="")
    col2.metric("💰 Gasto mes actual", f"${current_total:,.0f}", delta=f"{current_total - last_total:,.0f} vs. mes anterior")
    col3.metric("📅 Mes anterior", meses_es[last_month], delta="")
