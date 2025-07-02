import streamlit as st
import pandas as pd
import altair as alt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="Dashboard de Presupuesto", layout="wide")
st.title("📊 Dashboard de Presupuesto de Gastos")

# --- CONEXIÓN A GOOGLE SHEETS ---
@st.cache_data
def load_data():
    # Definir alcance y cargar credenciales
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("google_creds.json", scope)
    client = gspread.authorize(creds)

    # Abrir Google Sheet por ID
    sheet = client.open_by_key("1kVoN3RZgxaKeZ9Pe4RdaCg-5ugr37S8EKHVWhetG2Ao").sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    # Mostrar columnas originales
    st.write("🔍 Columnas desde Google Sheets:", df.columns.tolist())

    # Limpiar y renombrar columnas
    df.columns = df.columns.str.strip()  # elimina espacios ocultos
    df = df.rename(columns={
        "Fecha de Pago": "Fecha",
        "Banco": "Categoría"
    })

    # Mostrar columnas después del rename
    st.write("✅ Columnas luego del rename:", df.columns.tolist())

    # Convertir fechas
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    return df

# Cargar datos
df = load_data()

# Validación de columnas requeridas
required_columns = ["Fecha", "Categoría", "Concepto", "Monto", "Status"]
if not all(col in df.columns for col in required_columns):
    st.error("❌ El archivo no tiene las columnas requeridas.")
    st.stop()

# Crear columna de Mes
df["Mes"] = df["Fecha"].dt.strftime("%B")

# --- KPIs ---
col1, col2, col3 = st.columns(3)
total_gastado = df["Monto"].sum()
pagado = df[df["Status"] == "PAGADO"]["Monto"].sum()
por_pagar = df[df["Status"] != "PAGADO"]["Monto"].sum()
col1.metric("💰 Total Gastado", f"${total_gastado:,.0f}")
col2.metric("✅ Pagado", f"${pagado:,.0f}")
col3.metric("⚠️ Por Pagar", f"${por_pagar:,.0f}")
st.divider()

# --- FILTROS ---
meses = df["Mes"].dropna().unique()
categorias = df["Categoría"].unique()
colf1, colf2 = st.columns(2)
mes_sel = colf1.multiselect("📅 Filtrar por mes", sorted(meses), default=meses)
cat_sel = colf2.multiselect("🏦 Filtrar por categoría", sorted(categorias), default=categorias)
df_filtrado = df[df["Mes"].isin(mes_sel) & df["Categoría"].isin(cat_sel)]

# --- ALERTAS ---
pendientes = df_filtrado[df_filtrado["Status"] != "PAGADO"]
if not pendientes.empty:
    st.warning(f"🔔 Hay {len(pendientes)} conceptos pendientes de pago")
    with st.expander("Ver pendientes"):
        st.dataframe(pendientes)

# --- GRÁFICO: Gasto por Mes ---
st.subheader("📈 Gasto total por mes")
gasto_mes = df_filtrado.groupby("Mes")["Monto"].sum().reset_index()
chart_mes = alt.Chart(gasto_mes).mark_bar().encode(
    x=alt.X("Mes", sort=list(sorted(df["Mes"].unique()))),
    y="Monto",
    tooltip=["Mes", "Monto"]
)
st.altair_chart(chart_mes, use_container_width=True)

# --- GRÁFICO: Gasto por Categoría ---
st.subheader("🏦 Gasto por categoría")
gasto_cat = df_filtrado.groupby("Categoría")["Monto"].sum().reset_index().sort_values("Monto", ascending=False)
chart_cat = alt.Chart(gasto_cat).mark_bar().encode(
    x="Monto",
    y=alt.Y("Categoría", sort="-x"),
    tooltip=["Categoría", "Monto"]
)
st.altair_chart(chart_cat, use_container_width=True)

# --- TABLA FINAL ---
st.subheader("📄 Detalle de gastos filtrados")
st.dataframe(df_filtrado.sort_values("Fecha"))
