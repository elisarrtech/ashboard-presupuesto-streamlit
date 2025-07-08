import streamlit as st
import streamlit_authenticator as stauth
from calendar import month_name
import pandas as pd

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="📊 Dashboard de Presupuesto", layout="wide")
st.title("📊 Dashboard de Presupuesto de Gastos")

# Importaciones desde utils y components
from utils.data_loader import get_gsheet_data, save_gsheet_data, load_excel_data
from utils.data_processor import clean_and_validate_data, convert_df_to_csv
from components.visuals import (
    show_kpis,
    plot_gasto_por_mes,
    plot_gasto_por_categoria,
    show_filtered_table,
    show_month_comparison,
    show_categoria_presupuesto
)

# Diccionario de meses
meses_es = {i: month_name[i] for i in range(1, 13)}

# --- CARGA DE DATOS ---
data_source = st.sidebar.selectbox("🔍 Selecciona fuente de datos", ["Google Sheets", "Archivo CSV", "Archivo Excel"])

df = pd.DataFrame()
sheet = None

if data_source == "Google Sheets":
    try:
        df, sheet = get_gsheet_data()
    except Exception as e:
        st.error("❌ No se pudo conectar con Google Sheets. Verifica tus credenciales o conexión.")
        st.stop()
elif data_source == "Archivo CSV":
    uploaded_file = st.file_uploader("📁 Cargar archivo CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        # Normalización de columnas
        df.columns = [col.strip().capitalize() for col in df.columns]
        column_mapping = {'Mes': 'Fecha', 'Categoria': 'Categoría', 'Concepto': 'Concepto', 'Monto': 'Monto', 'Status': 'Status'}
        df.rename(columns=column_mapping, inplace=True)

        if st.checkbox("⬆️ Guardar en Google Sheets"):
            try:
                df_gs, sheet = get_gsheet_data()
                save_gsheet_data(sheet, df)
                st.success("✅ Datos cargados desde CSV y guardados en Google Sheets.")
            except Exception as e:
                st.error(f"❌ Error al guardar en Google Sheets: {e}")
elif data_source == "Archivo Excel":
    uploaded_file = st.file_uploader("📁 Cargar archivo Excel", type=["xlsx", "xls"])
    if uploaded_file:
        df = load_excel_data(uploaded_file)
        # Normalización de columnas
        df.columns = [col.strip().capitalize() for col in df.columns]
        column_mapping = {'Mes': 'Fecha', 'Categoria': 'Categoría', 'Concepto': 'Concepto', 'Monto': 'Monto', 'Status': 'Status'}
        df.rename(columns=column_mapping, inplace=True)

        if st.checkbox("⬆️ Guardar en Google Sheets"):
            try:
                df_gs, sheet = get_gsheet_data()
                save_gsheet_data(sheet, df)
                st.success("✅ Datos cargados desde Excel y guardados en Google Sheets.")
            except Exception as e:
                st.error(f"❌ Error al guardar en Google Sheets: {e}")

# --- LIMPIEZA Y VALIDACIÓN ---
if not df.empty:
    try:
        df = clean_and_validate_data(df)
    except ValueError as e:
        st.error(f"❌ Error en la validación de datos: {e}")
        st.stop()

    # --- VISUALIZACIONES ---
    show_kpis(df)
    plot_gasto_por_mes(df)
    plot_gasto_por_categoria(df)
    show_filtered_table(df)
    plot_gasto_por_categoria(df)
    show_month_comparison(df)
    show_categoria_presupuesto(df)
else:
    st.warning("⚠️ No hay datos para mostrar.")
