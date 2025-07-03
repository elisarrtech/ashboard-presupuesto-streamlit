# app.py
import streamlit as st
import pandas as pd
from calendar import month_name

# Importaciones desde utils y components
from utils.data_loader import get_gsheet_data, save_gsheet_data
from utils.data_processor import clean_and_validate_data, convert_df_to_csv
from components.sidebar import render_sidebar
from components.visuals import (
    show_kpis,
    plot_gasto_por_mes,
    plot_gasto_por_categoria,
    show_filtered_table,
    show_month_comparison,
    show_categoria_presupuesto
)

# Configuración inicial
st.set_page_config(page_title="📊 Dashboard de Presupuesto", layout="wide")
st.title("📊 Dashboard de Presupuesto de Gastos")

# Diccionario de meses
meses_es = {i: month_name[i] for i in range(1, 13)}

# Definición del presupuesto por categoría
presupuesto_categoria = {
    "Mercado": 5000,
    "Servicios": 3000,
    "Renta": 8000,
    "Transporte": 1500,
    "Ocio": 1000,
}

# --- CARGA DE DATOS ---
try:
    df, sheet = get_gsheet_data()
except Exception as e:
    st.error("❌ No se pudo conectar con Google Sheets. Verifica tus credenciales o conexión.")
    st.stop()

st.write("Categorías únicas en tus datos:", df["Categoría"].unique())

# --- CARGA MANUAL OPCIONAL ---
uploaded_file = st.file_uploader("📁 Cargar archivo CSV (opcional)", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    try:
        save_gsheet_data(sheet, df)
        st.success("✅ Datos cargados desde CSV y guardados en Google Sheets.")
    except Exception as e:
        st.error(f"❌ Error al guardar en Google Sheets: {e}")

    # Mostrar columnas actuales para depuración
    st.write("Columnas actuales:", list(df.columns))

# --- LIMPIEZA Y VALIDACIÓN ---
try:
    df = clean_and_validate_data(df)
except ValueError as ve:
    st.error(str(ve))
    st.stop()

# --- SIDEBAR: CRUD ---
render_sidebar(df, sheet)

# --- FILTROS ---
meses = list(meses_es.values())
categorias = df["Categoría"].dropna().unique()
colf1, colf2 = st.columns(2)
mes_sel = colf1.multiselect("📅 Filtrar por mes", meses, default=meses)
cat_sel = colf2.multiselect("🏦 Filtrar por categoría", sorted(categorias), default=categorias)

df_filtrado = df[df["Mes"].isin(mes_sel) & df["Categoría"].isin(cat_sel)]

# --- DESCARGA DE DATOS FILTRADOS ---
st.subheader("⬇️ Descargar datos filtrados")
csv = convert_df_to_csv(df_filtrado)
st.download_button(
    label="📥 Descargar CSV",
    data=csv,
    file_name="datos_presupuesto_filtrados.csv",
    mime="text/csv"
)

# --- COMPARACIÓN MENSUAL ---
show_month_comparison(df_filtrado)

# --- KPIs ---
show_kpis(df)

# --- GRÁFICOS Y TABLA FINAL ---
plot_gasto_por_mes(df_filtrado)
plot_gasto_por_categoria(df_filtrado)
show_filtered_table(df_filtrado)

# --- PRESUPUESTO POR CATEGORÍA ---
df_presupuesto = show_categoria_presupuesto(df_filtrado, presupuesto_categoria)

# --- ALERTAS ---
st.subheader("⚠️ Alertas de Presupuesto Excedido")
alertas = df_presupuesto[df_presupuesto["Diferencia"] > 0]

if not alertas.empty:
    for _, row in alertas.iterrows():
        st.error(f"🔴 Categoría '{row['Categoría']}' excedió el presupuesto en ${row['Diferencia']:,.0f}")
else:
    st.success("✅ Todas las categorías están dentro del presupuesto.")

# --- SELECCIÓN DINÁMICA DE CATEGORÍAS Y PRESUPUESTO ---
st.sidebar.subheader("🎯 Selecciona categorías para comparar")

# Obtener categorías únicas del DataFrame filtrado
categorias_unicas = df_filtrado["Categoría"].dropna().unique()

# Mostrar multiselect para elegir las categorías a comparar
categorias_seleccionadas = st.sidebar.multiselect(
    "Categorías disponibles", 
    sorted(categorias_unicas), 
    default=sorted(categorias_unicas)
)

# Permitir al usuario ingresar el presupuesto por categoría
presupuesto_categoria = {}
for cat in categorias_seleccionadas:
    presupuesto = st.sidebar.number_input(
        f"Presupuesto para {cat}", 
        min_value=0.0, 
        value=1000.0, 
        key=f"pres_{cat}"
    )
    presupuesto_categoria[cat] = presupuesto
