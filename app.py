# app.py
import streamlit as st
import pandas as pd
from utils.data_loader import get_gsheet_data
from utils.data_processor import clean_and_validate_data
from components.sidebar import render_sidebar
from components.visuals import show_kpis, plot_gasto_por_mes, plot_gasto_por_categoria, show_filtered_table

st.set_page_config(page_title="📊 Dashboard de Presupuesto", layout="wide")
st.title("📊 Dashboard de Presupuesto de Gastos")

# --- CARGA DE DATOS ---
try:
    df, sheet = get_gsheet_data()
except Exception as e:
    st.error("❌ No se pudo conectar con Google Sheets. Verifica tus credenciales o conexión.")
    st.stop()

# --- CARGA MANUAL OPCIONAL ---
uploaded_file = st.file_uploader("📁 Cargar archivo CSV (opcional)", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    try:
        from utils.data_loader import save_gsheet_data
        save_gsheet_data(sheet, df)
        st.success("✅ Datos cargados desde CSV y guardados en Google Sheets.")
    except Exception as e:
        st.error("❌ Error al guardar en Google Sheets.")

# --- LIMPIEZA Y VALIDACIÓN ---
try:
    df = clean_and_validate_data(df)
except ValueError as ve:
    st.error(str(ve))
    st.stop()

# --- SIDEBAR: CRUD ---
render_sidebar(df, sheet)

# --- FILTROS ---
meses_es = {i: month_name[i] for i in range(1, 13)}
meses = list(meses_es.values())
categorias = df["Categoría"].dropna().unique()
colf1, colf2 = st.columns(2)
mes_sel = colf1.multiselect("📅 Filtrar por mes", meses, default=meses)
cat_sel = colf2.multiselect("🏦 Filtrar por categoría", sorted(categorias), default=categorias)

df_filtrado = df[df["Mes"].isin(mes_sel) & df["Categoría"].isin(cat_sel)]

# --- VISUALIZACIONES ---
show_kpis(df)
plot_gasto_por_mes(df_filtrado)
plot_gasto_por_categoria(df_filtrado)
show_filtered_table(df_filtrado)
