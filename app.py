import streamlit as st
import pandas as pd
import altair as alt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from calendar import month_name
import json
import os

st.set_page_config(page_title="Dashboard de Presupuesto", layout="wide")
st.title("📊 Dashboard de Presupuesto de Gastos")

# --- FUNCIÓN PARA AUTORIZAR GOOGLE SHEETS DESDE SECRETS ---
def authorize_google_sheets():
    creds_dict = json.loads(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict)
    client = gspread.authorize(creds)
    return client

# --- CARGA MANUAL OPCIONAL ---
uploaded_file = st.file_uploader("📁 Cargar archivo CSV (opcional)", type="csv")

# --- FUNCIÓN PARA LEER DESDE GOOGLE SHEETS ---
def load_google_sheet():
    client = authorize_google_sheets()
    sheet = client.open_by_key("1kVoN3RZgxaKeZ9Pe4RdaCg-5ugr37S8EKHVWhetG2Ao").sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

# --- CARGAR DATOS: CSV tiene prioridad si se sube ---
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(uploaded_file, encoding='latin1')
        except Exception as e:
            st.error(f"❌ No se pudo leer el archivo. Error: {e}")
            st.stop()
    st.success("✅ Datos cargados desde archivo CSV.")
else:
    try:
        df = load_google_sheet()
        st.success("✅ Datos cargados desde Google Sheets.")
    except Exception as e:
        st.error(f"❌ Error al cargar desde Google Sheets: {e}")
        st.stop()

# --- LIMPIEZA Y VALIDACIÓN ---
df.columns = df.columns.str.strip()
df = df.rename(columns={"Fecha de Pago": "Fecha", "Banco": "Categoría"})
df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

required_columns = ["Fecha", "Categoría", "Concepto", "Monto", "Status"]
if not all(col in df.columns for col in required_columns):
    st.error("❌ El archivo no tiene las columnas requeridas.")
    st.stop()

# --- EXTRAER MES EN ESPAÑOL ---
meses_es = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}
df["Mes"] = df["Fecha"].dt.month.map(meses_es)

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

# --- ALERTAS ---
pendientes = df_filtrado[df_filtrado["Status"] != "PAGADO"]
if not pendientes.empty:
    st.warning(f"🔔 Hay {len(pendientes)} conceptos pendientes de pago")
    with st.expander("Ver pendientes"):
        st.dataframe(pendientes)

# --- GRÁFICO: Gasto por Mes ---
st.subheader("📈 Gasto total por mes")
gasto_mes = df_filtrado.groupby("Mes")["Monto"].sum().reset_index()
gasto_mes["Mes"] = pd.Categorical(gasto_mes["Mes"], categories=meses, ordered=True)
gasto_mes = gasto_mes.sort_values("Mes")

chart_mes = alt.Chart(gasto_mes).mark_bar().encode(
    x=alt.X("Mes", sort=meses, title="Mes"),
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


# --- MÓDULO DE EDICIÓN DE REGISTROS ---
st.header("✏️ Editar registros existentes")

try:
    df_edicion = load_google_sheet()
    df_edicion["Identificador"] = df_edicion.index.astype(str) + " - " + df_edicion["Concepto"]

    selected_id = st.selectbox("🔎 Selecciona un registro para editar", df_edicion["Identificador"])

    if selected_id:
        index_to_edit = int(selected_id.split(" - ")[0])
        row_data = df_edicion.loc[index_to_edit]

        with st.form(key="edit_form"):
            nueva_fecha = st.date_input("📅 Fecha", value=pd.to_datetime(row_data["Fecha"]))
            nueva_categoria = st.text_input("🏦 Categoría", value=row_data["Categoría"])
            nuevo_concepto = st.text_input("📝 Concepto", value=row_data["Concepto"])
            nuevo_monto = st.number_input("💵 Monto", min_value=0.0, value=float(row_data["Monto"]))
            nuevo_status = st.selectbox("📌 Status", ["PAGADO", "PENDIENTE"], index=["PAGADO", "PENDIENTE"].index(row_data["Status"]))
            guardar = st.form_submit_button("💾 Guardar cambios")

        if guardar:
            df_edicion.at[index_to_edit, "Fecha"] = nueva_fecha.strftime("%Y-%m-%d")
            df_edicion.at[index_to_edit, "Categoría"] = nueva_categoria
            df_edicion.at[index_to_edit, "Concepto"] = nuevo_concepto
            df_edicion.at[index_to_edit, "Monto"] = nuevo_monto
            df_edicion.at[index_to_edit, "Status"] = nuevo_status
            df_edicion.at[index_to_edit, "Mes"] = meses_es[nueva_fecha.month]

            sheet = gspread.authorize(
                ServiceAccountCredentials.from_json_keyfile_name("google_creds.json", scope)
            ).open_by_key(sheet_id).sheet1

            sheet.clear()
            sheet.update([df_edicion.columns.values.tolist()] + df_edicion.values.tolist())

            st.success("✅ Registro editado correctamente.")
            st.experimental_rerun()

except Exception as e:
    st.error(f"❌ Error al cargar módulo de edición: {e}")
