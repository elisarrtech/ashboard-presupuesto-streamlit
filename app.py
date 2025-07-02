import streamlit as st
import pandas as pd
import altair as alt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from calendar import month_name

st.set_page_config(page_title="Dashboard de Presupuesto", layout="wide")
st.title("📊 Dashboard de Presupuesto de Gastos")

# --- CARGA MANUAL OPCIONAL ---
uploaded_file = st.file_uploader("📁 Cargar archivo CSV (opcional)", type="csv")

# --- FUNCIÓN PARA LEER DESDE GOOGLE SHEETS ---
def load_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("google_creds.json", scope)
    client = gspread.authorize(creds)
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

# --- FORMULARIO PARA AGREGAR NUEVOS REGISTROS ---
st.subheader("➕ Agregar nuevo gasto manualmente")

with st.form("formulario_nuevo_gasto"):
    col_a, col_b = st.columns(2)
    fecha_nueva = col_a.date_input("📅 Fecha de Pago", value=datetime.today())
    categoria_nueva = col_b.text_input("🏦 Categoría (Banco, cuenta, tarjeta)", "")

    concepto_nuevo = st.text_input("📝 Concepto", "")
    monto_nuevo = st.number_input("💵 Monto", min_value=0.0, step=0.01)
    status_nuevo = st.selectbox("📌 Status", ["PAGADO", "PENDIENTE"])

    submitted = st.form_submit_button("✅ Agregar gasto")

if submitted:
    nuevo = {
        "Fecha": pd.to_datetime(fecha_nueva),
        "Categoría": categoria_nueva.strip().upper(),
        "Concepto": concepto_nuevo.strip().capitalize(),
        "Monto": monto_nuevo,
        "Status": status_nuevo
    }

    df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
    st.success("✅ Gasto agregado correctamente.")


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

# =========================
# FORMULARIO PARA NUEVO REGISTRO
# =========================
st.header("📝 Agregar nuevo registro de gasto")

with st.form("formulario_gasto"):
    col1, col2 = st.columns(2)
    fecha = col1.date_input("📅 Fecha del gasto", value=datetime.today())
    categoria = col2.text_input("🏦 Categoría", placeholder="Ej. SANTANDER")

    concepto = st.text_input("🧾 Concepto del gasto", placeholder="Ej. Pago de tarjeta")
    monto = st.number_input("💲 Monto", min_value=0.0, step=10.0)
    status = st.selectbox("📌 Estatus del gasto", options=["PAGADO", "PENDIENTE"])

    submit = st.form_submit_button("➕ Agregar registro")

if submit:
    try:
        # Cálculo automático del mes
        mes = fecha.strftime("%B")

        # Crear diccionario del nuevo registro
        nuevo_registro = {
            "Fecha": fecha.strftime("%Y-%m-%d"),
            "Categoría": categoria.strip(),
            "Concepto": concepto.strip(),
            "Monto": monto,
            "Status": status,
            "Mes": mes
        }

        # Conectarse y agregar fila
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("google_creds.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key("1kVoN3RZgxaKeZ9Pe4RdaCg-5ugr37S8EKHVWhetG2Ao").sheet1

        sheet.append_row(list(nuevo_registro.values()))
        st.success("✅ Registro agregado correctamente")

        # Recargar datos para que se vea reflejado
        st.experimental_rerun()

    except Exception as e:
        st.error(f"❌ No se pudo guardar el registro: {e}")

# --- MÓDULO DE EDICIÓN DE REGISTROS ---
st.header("✏️ Editar registros existentes")

try:
    # Recargar datos actualizados
    df_edicion = load_google_sheet()

    # Selector de fila por índice o concepto
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
            submit = st.form_submit_button("💾 Guardar cambios")

        if submit:
            # Actualizamos los valores
            df_edicion.at[index_to_edit, "Fecha"] = nueva_fecha.strftime("%Y-%m-%d")
            df_edicion.at[index_to_edit, "Categoría"] = nueva_categoria
            df_edicion.at[index_to_edit, "Concepto"] = nuevo_concepto
            df_edicion.at[index_to_edit, "Monto"] = nuevo_monto
            df_edicion.at[index]()_

# --- MÓDULO PARA AGREGAR NUEVOS REGISTROS ---
st.header("➕ Agregar nuevo gasto")

with st.form("form_nuevo_gasto"):
    fecha_nueva = st.date_input("📅 Fecha del gasto", value=datetime.today())
    categoria_nueva = st.text_input("🏦 Categoría", placeholder="Ej. SANTANDER")
    concepto_nuevo = st.text_input("📝 Concepto", placeholder="Ej. Pago mensual tarjeta")
    monto_nuevo = st.number_input("💵 Monto", min_value=0.0, step=100.0)
    status_nuevo = st.selectbox("📌 Status", ["PAGADO", "PENDIENTE"])
    boton_guardar = st.form_submit_button("✅ Guardar nuevo gasto")

if boton_guardar:
    try:
        # Cargar datos actuales
        df_actual = load_google_sheet()

        # Crear nuevo registro
        nuevo_registro = {
            "Fecha": fecha_nueva.strftime("%Y-%m-%d"),
            "Categoría": categoria_nueva,
            "Concepto": concepto_nuevo,
            "Monto": monto_nuevo,
            "Status": status_nuevo,
            "Mes": fecha_nueva.strftime("%B")
        }

        df_actual = df_actual.append(nuevo_registro, ignore_index=True)

        # Guardar en Google Sheets
        sheet = gspread.authorize(
            ServiceAccountCredentials.from_json_keyfile_name("google_creds.json", scope)
        ).open_by_key("1kVoN3RZgxaKeZ9Pe4RdaCg-5ugr37S8EKHVWhetG2Ao").sheet1

        sheet.clear()
        sheet.update([df_actual.columns.values.tolist()] + df_actual.values.tolist())

        st.success("✅ Gasto agregado exitosamente.")
    except Exception as e:
        st.error(f"❌ Error al guardar el nuevo gasto: {e}")
