import streamlit as st
import pandas as pd
from calendar import month_name
from utils.data_loader import get_gsheet_data, save_gsheet_data, load_excel_data
from utils.data_processor import clean_and_validate_data
from components.visuals import (
    show_kpis,
    plot_gasto_por_mes,
    plot_gasto_por_categoria,
    show_filtered_table,
    show_month_comparison,
    show_categoria_presupuesto,
    show_monthly_topes
)

st.set_page_config(page_title="Presupuesto", layout="wide")

# Configuración inicial
meses_es = {i: month_name[i] for i in range(1, 13)}
topes_mensuales = {1: 496861.12, 2: 534961.49, 3: 492482.48, 4: 442578.28, 5: 405198.44, 6: 416490.46, 7: 420000.00}

# Selección fuente de datos
data_source = st.sidebar.selectbox("Fuente de datos", ["Google Sheets", "Archivo Excel"])
df = pd.DataFrame()

if data_source == "Google Sheets":
    try:
        df, sheet = get_gsheet_data()
    except Exception as e:
        st.error("Error al conectar con Google Sheets")
        st.stop()

elif data_source == "Archivo Excel":
    uploaded_file = st.file_uploader("Subir archivo Excel", type=["xlsx", "xls"])
    if uploaded_file:
        df = load_excel_data(uploaded_file)
        df = df.loc[:, ~df.columns.duplicated()]  # Eliminar columnas duplicadas

# Si hay datos cargados
if not df.empty:
    df.columns = [col.strip().capitalize() for col in df.columns]
    df.rename(columns={"Mes": "Fecha", "Categoria": "Categoría", "Concepto": "Concepto", "Monto": "Monto", "Status": "Status"}, inplace=True)

    df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce')
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')

    # Agregar columnas de mes
    df["Mes_num"] = df["Fecha"].dt.month
    df["Mes"] = df["Mes_num"].map(meses_es)

    try:
        df = clean_and_validate_data(df)
    except ValueError as e:
        st.error(f"Error validando datos: {e}")
        st.stop()

    filtro_mes = st.sidebar.multiselect("Filtrar por mes", options=list(range(1, 13)), format_func=lambda x: meses_es[x])
    if filtro_mes:
        df = df[df["Mes_num"].isin(filtro_mes)]

    # Visualizaciones
    show_kpis(df, topes_mensuales, filtro_mes)
    plot_gasto_por_mes(df, filtro_mes)
    show_monthly_topes(df, topes_mensuales, filtro_mes)
    plot_gasto_por_categoria(df, filtro_mes)
    show_filtered_table(df)
    show_month_comparison(df)
    show_categoria_presupuesto(df, presupuesto_categoria={})

else:
    st.warning("No hay datos para mostrar.")
