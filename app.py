import streamlit as st
import pandas as pd
import altair as alt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from calendar import month_name
import json

st.set_page_config(page_title="Dashboard de Presupuesto", layout="wide")
st.title("📊 Dashboard de Presupuesto de Gastos")

# --- CONEXIÓN A GOOGLE SHEETS ---
def get_gsheet_data():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = json.loads(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key("1kVoN3RZgxaKeZ9Pe4RdaCg-5ugr37S8EKHVWhetG2Ao").sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data), sheet

def save_gsheet_data(sheet, df):
    sheet.clear()
    sheet.update([list(map(str, df.columns))] + df.astype(str).values.tolist())

# --- CARGA MANUAL OPCIONAL ---
uploaded_file = st.file_uploader("📁 Cargar archivo CSV (opcional)", type="csv")

df, sheet = get_gsheet_data()

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    save_gsheet_data(sheet, df)
    st.success("✅ Datos cargados desde archivo CSV y guardados en Google Sheets.")

# --- LIMPIEZA Y VALIDACIÓN ---
df.columns = df.columns.str.strip()
df = df.rename(columns={"Fecha de Pago": "Fecha", "Banco": "Categoría"})
df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

required_columns = ["Fecha", "Categoría", "Concepto", "Monto", "Status"]
if not all(col in df.columns for col in required_columns):
    st.error("❌ El archivo no tiene las columnas requeridas.")
    st.stop()

# --- EXTRAER MES EN ESPAÑOL ---
meses_es = {i: month_name[i] for i in range(1, 13)}
df["Mes"] = df["Fecha"].dt.month.map(meses_es)

# --- CRUD (AGREGAR Y EDITAR) ---
st.sidebar.header("➕ Agregar / ✏️ Editar Concepto")
modo = st.sidebar.radio("Modo", ["Agregar", "Editar"])

if modo == "Agregar":
    with st.sidebar.form("Agregar Concepto"):
        fecha = st.date_input("Fecha", value=datetime.today())
        categoria = st.text_input("Categoría")
        concepto = st.text_input("Concepto")
        monto = st.number_input("Monto", min_value=0.0)
        status = st.selectbox("Status", ["PAGADO", "PENDIENTE"])
        submit = st.form_submit_button("Guardar")

    if submit:
        nuevo = pd.DataFrame.from_dict([{
            "Fecha": fecha,
            "Categoría": categoria,
            "Concepto": concepto,
            "Monto": monto,
            "Status": status,
            "Mes": meses_es[fecha.month]
        }])
        df = pd.concat([df, nuevo], ignore_index=True)
        save_gsheet_data(sheet, df)
        st.success("✅ Concepto agregado correctamente.")

elif modo == "Editar":
    fila = st.sidebar.number_input("Número de fila a editar", min_value=0, max_value=len(df)-1, step=1)
    with st.sidebar.form("Editar Concepto"):
        fecha = st.date_input("Fecha", value=df.loc[fila, "Fecha"])
        categoria = st.text_input("Categoría", value=df.loc[fila, "Categoría"])
        concepto = st.text_input("Concepto", value=df.loc[fila, "Concepto"])
        monto = st.number_input("Monto", min_value=0.0, value=float(df.loc[fila, "Monto"]))
        status = st.selectbox("Status", ["PAGADO", "PENDIENTE"], index=0 if df.loc[fila, "Status"] == "PAGADO" else 1)
        submit = st.form_submit_button("Actualizar")

    if submit:
        df.at[fila, "Fecha"] = fecha
        df.at[fila, "Categoría"] = categoria
        df.at[fila, "Concepto"] = concepto
        df.at[fila, "Monto"] = monto
        df.at[fila, "Status"] = status
        df.at[fila, "Mes"] = meses_es[fecha.month]
        save_gsheet_data(sheet, df)
        st.success("✅ Concepto actualizado correctamente.")

# --- KPIs ---
col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Gastado", f"${df['Monto'].sum():,.0f}")
col2.metric("✅ Pagado", f"${df[df['Status'] == 'PAGADO']['Monto'].sum():,.0f}")
col3.metric("⚠️ Por Pagar", f"${df[df['Status'] != 'PAGADO']['Monto'].sum():,.0f}")
st.divider()

# --- FILTROS ---
meses = list(meses_es.values())
categorias = df["Categoría"].dropna().unique()
colf1, colf2 = st.columns(2)
mes_sel = colf1.multiselect("📅 Filtrar por mes", meses, default=meses)
cat_sel = colf2.multiselect("🏦 Filtrar por categoría", sorted(categorias), default=categorias)

df_filtrado = df[df["Mes"].isin(mes_sel) & df["Categoría"].isin(cat_sel)]

# --- GRÁFICO: Gasto por Mes ---
st.subheader("📈 Gasto total por mes")
gasto_mes = df_filtrado.groupby("Mes")["Monto"].sum().reset_index()
gasto_mes = gasto_mes.sort_values("Mes")

chart_mes = alt.Chart(gasto_mes).mark_bar().encode(
    x=alt.X("Mes", title="Mes"),
    y=alt.Y("Monto", title="Monto Total"),
    tooltip=["Mes", "Monto"]
)
st.altair_chart(chart_mes, use_container_width=True)

# --- GRÁFICO: Gasto por Categoría ---
st.subheader("🏦 Gasto por categoría")
gasto_cat = df_filtrado.groupby("Categoría")["Monto"].sum().reset_index().sort_values("Monto", ascending=False)
st.altair_chart(alt.Chart(gasto_cat).mark_bar().encode(
    x="Monto",
    y=alt.Y("Categoría", sort="-x"),
    tooltip=["Categoría", "Monto"]
), use_container_width=True)

# --- TABLA FINAL ---
st.subheader("📄 Detalle de gastos filtrados")
st.dataframe(df_filtrado.sort_values("Fecha"))
