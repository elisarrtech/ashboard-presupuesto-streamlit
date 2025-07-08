import streamlit as st
import pandas as pd
from calendar import month_name
from utils.data_loader import get_gsheet_data, save_gsheet_data, load_excel_data
from utils.data_processor import clean_and_validate_data, convert_df_to_csv
from components.visuals import (
    show_kpis,
    plot_gasto_por_mes,
    plot_gasto_por_categoria,
    show_filtered_table,
    show_month_comparison,
    show_categoria_presupuesto,
    show_monthly_topes,
    show_nominas_comisiones
)

st.set_page_config(page_title="Presupuesto", layout="wide")

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
        df = df.loc[:, ~df.columns.duplicated()]

# Si hay datos cargados
if not df.empty:
    df = clean_and_validate_data(df)

    pagina = st.sidebar.radio("Selecciona sección", ["General", "Nóminas y Comisiones"])

    filtro_mes = st.sidebar.multiselect("📅 Filtrar por mes", options=list(range(1, 13)), format_func=lambda x: month_name[x])
    filtro_categoria = st.sidebar.multiselect("📂 Filtrar por categoría", options=df["Categoría"].dropna().unique())
    filtro_banco = st.sidebar.multiselect("🏦 Filtrar por banco", options=df["Banco"].dropna().unique())
    filtro_status = st.sidebar.multiselect("✅ Filtrar por estado", options=df["Status"].dropna().unique())

    if filtro_mes:
        df = df[df["Mes_num"].isin(filtro_mes)]
    if filtro_categoria:
        df = df[df["Categoría"].isin(filtro_categoria)]
    if filtro_banco:
        df = df[df["Banco"].isin(filtro_banco)]
    if filtro_status:
        df = df[df["Status"].isin(filtro_status)]

    if pagina == "General":
        show_kpis(df, topes_mensuales, filtro_mes)
        plot_gasto_por_mes(df, filtro_mes)
        show_monthly_topes(df, topes_mensuales, filtro_mes)
        plot_gasto_por_categoria(df, filtro_mes)
        show_filtered_table(df)
        show_month_comparison(df)
        show_categoria_presupuesto(df, presupuesto_categoria={})

        st.download_button("⬇️ Descargar CSV", convert_df_to_csv(df), file_name="presupuesto_filtrado.csv", mime="text/csv")
        st.download_button("⬇️ Descargar Excel", convert_df_to_csv(df), file_name="presupuesto_filtrado.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    elif pagina == "Nóminas y Comisiones":
        show_nominas_comisiones(df, filtro_mes)

else:
    st.warning("No hay datos para mostrar.")
