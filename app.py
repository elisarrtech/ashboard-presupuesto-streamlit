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
    show_categoria_presupuesto,
    show_monthly_topes
)

# Diccionario de meses
df_deudas = pd.DataFrame({
    "DEUDAS": ["RENTA", "HONORARIOS CONTADOR", "LENIN"],
    "MONTO": [300000.00, 200000.00, 55000.00],
    "IVA": [48000.00, 32000.00, 8800.00],
    "TOTAL": [348000.00, 232000.00, 63800.00]
})

meses_es = {i: month_name[i] for i in range(1, 13)}

# --- Topes mensuales ---
topes_mensuales = {
    1: 496861.12,
    2: 534961.49,
    3: 492482.48,
    4: 442578.28,
    5: 405198.44,
    6: 416490.46,
    7: 420000.00,
}

# --- FILTRO DE PÁGINAS ---
pagina = st.sidebar.radio("Selecciona sección", ["Presupuesto", "Deudas", "Nóminas y Comisiones"])

if pagina == "Deudas":
    st.header("💸 Deudas")
    edited_df = st.experimental_data_editor(df_deudas, num_rows="dynamic")
    st.write("### Estado de deudas actualizado:")
    st.dataframe(edited_df)

elif pagina == "Nóminas y Comisiones":
    st.header("💼 Nóminas y Comisiones")

    df, sheet = get_gsheet_data()

    if not df.empty:
        df = clean_and_validate_data(df)
        df_nominas = df[df['Categoría'].str.contains("nómina|comisión", case=False, na=False)]

        filtro_mes = st.sidebar.multiselect("📅 Filtrar por mes", options=list(range(1, 13)), format_func=lambda x: meses_es[x])

        if filtro_mes:
            df_nominas = df_nominas[df_nominas["Mes_num"].isin(filtro_mes)]

        show_kpis(df_nominas, topes_mensuales, filtro_mes)
        plot_gasto_por_mes(df_nominas, filtro_mes)
        show_monthly_topes(df_nominas, topes_mensuales, filtro_mes)
        plot_gasto_por_categoria(df_nominas, filtro_mes)
        show_filtered_table(df_nominas)
        show_month_comparison(df_nominas)
        show_categoria_presupuesto(df_nominas, presupuesto_categoria={})

    else:
        st.warning("⚠️ No hay datos para mostrar.")

else:
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
            df.columns = [col.strip().capitalize() for col in df.columns]
            column_mapping = {'Mes': 'Fecha', 'Categoria': 'Categoría', 'Concepto': 'Concepto', 'Monto': 'Monto', 'Status': 'Status'}
            df.rename(columns=column_mapping, inplace=True)
            df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce')
            df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')

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
            df.columns = [col.strip().capitalize() for col in df.columns]
            column_mapping = {'Mes': 'Fecha', 'Categoria': 'Categoría', 'Concepto': 'Concepto', 'Monto': 'Monto', 'Status': 'Status'}
            df.rename(columns=column_mapping, inplace=True)
            df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce')
            df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')

            if st.checkbox("⬆️ Guardar en Google Sheets"):
                try:
                    df_gs, sheet = get_gsheet_data()
                    save_gsheet_data(sheet, df)
                    st.success("✅ Datos cargados desde Excel y guardados en Google Sheets.")
                except Exception as e:
                    st.error(f"❌ Error al guardar en Google Sheets: {e}")

    filtro_mes = st.sidebar.multiselect("📅 Filtrar por mes", options=list(range(1, 13)), format_func=lambda x: meses_es[x])

    if not df.empty:
        try:
            df = clean_and_validate_data(df)
        except ValueError as e:
            st.error(f"❌ Error en la validación de datos: {e}")
            st.stop()

        if filtro_mes:
            df = df[df["Mes_num"].isin(filtro_mes)]

        show_kpis(df, topes_mensuales, filtro_mes)
        plot_gasto_por_mes(df, filtro_mes)
        show_monthly_topes(df, topes_mensuales, filtro_mes)
        plot_gasto_por_categoria(df, filtro_mes)
        show_filtered_table(df)
        show_month_comparison(df)
        show_categoria_presupuesto(df, presupuesto_categoria={})

    else:
        st.warning("⚠️ No hay datos para mostrar.")
