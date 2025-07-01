import streamlit as st
import pandas as pd
import plotly.express as px
import io
from pandas import ExcelWriter
from datetime import date
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# ---------------- CONFIGURACIÓN INICIAL ----------------
st.set_page_config(page_title="Dashboard de Presupuesto", layout="wide")

# ---------------- AUTENTICACIÓN ----------------
def autenticar():
    st.sidebar.title("🔐 Autenticación")
    usuario = st.sidebar.text_input("Usuario", value="", key="usuario")
    contraseña = st.sidebar.text_input("Contraseña", type="password", value="", key="contraseña")

    usuario_valido = st.secrets["auth"]["usuario"]
    contraseña_valida = st.secrets["auth"]["password"]

    if usuario == usuario_valido and contraseña == contraseña_valida:
        return True
    else:
        if usuario and contraseña:
            st.sidebar.error("❌ Usuario o contraseña incorrectos.")
        return False

if not autenticar():
    st.stop()

# ---------------- FUNCIÓN PARA GUARDAR EN GOOGLE SHEETS ----------------
def guardar_en_google_sheets(datos: dict):
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    SHEET_ID = "1kVoN3RZgxaKeZ9Pe4RdaCg-5ugr37S8EKHVWhetG2Ao"
    sheet = client.open_by_key(SHEET_ID).sheet1
    fila = [
        datos["Año"], datos["Fecha"], datos["Categoría"], datos["Subcategoría"],
        datos["Concepto"], datos["Monto"], datos["Aplica IVA"], datos["IVA"], datos["Total c/IVA"]
    ]
    sheet.append_row(fila, value_input_option="USER_ENTERED")

# ---------------- TABS PRINCIPALES ----------------
tab1, tab2 = st.tabs(["📊 Dashboard Actual", "🗃 Historial de Conceptos Guardados"])

# ---------------- TAB 1: DASHBOARD ACTUAL ----------------
with tab1:
    uploaded_file = st.file_uploader("📁 Cargar archivo CSV", type=["csv"])
    if uploaded_file is None:
        st.warning("🔄 Por favor carga un archivo CSV para iniciar.")
        st.stop()

    df = pd.read_csv(uploaded_file)

    columnas_requeridas = {"Año", "Categoría", "Subcategoría", "Concepto", "Monto", "Aplica IVA"}
    if not columnas_requeridas.issubset(df.columns):
        st.error("❌ El archivo no tiene las columnas requeridas.")
        st.stop()

    if "IVA" not in df.columns:
        df["IVA"] = df.apply(lambda row: row["Monto"] * 0.16 if row["Aplica IVA"] == "Sí" else 0, axis=1)

    if "Total c/IVA" not in df.columns:
        df["Total c/IVA"] = df["Monto"] + df["IVA"]

    if "Fecha" in df.columns:
        df["Fecha"] = pd.to_datetime(df["Fecha"])
        df["Mes"] = df["Fecha"].dt.to_period("M").astype(str)
    else:
        df["Fecha"] = pd.NaT
        df["Mes"] = "Sin Fecha"

    st.sidebar.markdown("### 📝 Agregar nuevo concepto")
    with st.sidebar.form("formulario_concepto"):
        anio = st.number_input("Año", min_value=2000, max_value=2100, step=1, value=2025)
        fecha = st.date_input("Fecha del gasto", value=date.today())
        categoria = st.text_input("Categoría")
        subcategoria = st.text_input("Subcategoría")
        concepto = st.text_input("Nombre del concepto")
        monto = st.number_input("Monto", min_value=0.0, step=100.0)
        aplica_iva = st.selectbox("¿Aplica IVA?", ["Sí", "No"])
        submitted = st.form_submit_button("➕ Agregar concepto")

    if submitted:
        if not categoria or not concepto or monto == 0:
            st.warning("⚠️ Por favor completa todos los campos obligatorios.")
        else:
            nuevo = {
                "Año": anio,
                "Fecha": fecha.strftime("%Y-%m-%d"),
                "Categoría": categoria,
                "Subcategoría": subcategoria,
                "Concepto": concepto,
                "Monto": monto,
                "Aplica IVA": aplica_iva,
            }
            nuevo["IVA"] = monto * 0.16 if aplica_iva == "Sí" else 0
            nuevo["Total c/IVA"] = monto + nuevo["IVA"]
            df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
            guardar_en_google_sheets(nuevo)
            st.success("✅ Concepto agregado y guardado en Google Sheets")

    st.sidebar.markdown("### 🔍 Filtros")
    year = st.selectbox("Año", sorted(df["Año"].unique()))
    categoria_filtro = st.multiselect("Categoría", df["Categoría"].unique(), default=df["Categoría"].unique())
    filtered_df = df[(df["Año"] == year) & (df["Categoría"].isin(categoria_filtro))]

    st.markdown("### 📌 Indicadores Clave")
    col1, col2, col3 = st.columns(3)
    col1.metric("💼 Total Presupuesto", f"${filtered_df['Monto'].sum():,.2f}")
    col2.metric("🧾 Total IVA", f"${filtered_df['IVA'].sum():,.2f}")
    col3.metric("📊 Total con IVA", f"${filtered_df['Total c/IVA'].sum():,.2f}")
    st.markdown("---")

    pastel_colors = px.colors.qualitative.Pastel

    st.subheader("📈 Distribución por Subcategoría")
    fig1 = px.pie(filtered_df, names="Subcategoría", values="Total c/IVA", title="Total con IVA por Subcategoría", color_discrete_sequence=pastel_colors)
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("📊 Comparativa por Categoría")
    fig2 = px.bar(filtered_df, x="Categoría", y="Total c/IVA", color="Categoría", title="Totales con IVA por Categoría", color_discrete_sequence=pastel_colors)
    st.plotly_chart(fig2, use_container_width=True)

    if "Fecha" in filtered_df.columns and pd.notnull(filtered_df["Fecha"]).any():
        st.subheader("📆 Evolución del presupuesto por Mes")
        evolution_df = filtered_df.copy()
        evolution_df["Fecha"] = pd.to_datetime(evolution_df["Fecha"])
        evolution_df["Mes"] = evolution_df["Fecha"].dt.to_period("M").astype(str)
        fig3 = px.line(evolution_df.sort_values("Fecha"), x="Mes", y="Total c/IVA", color="Categoría", markers=True, color_discrete_sequence=pastel_colors)
        st.plotly_chart(fig3, use_container_width=True)

    buffer = io.BytesIO()
    with ExcelWriter(buffer, engine='xlsxwriter') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name="Presupuesto")

    st.download_button(
        label="⬇ Descargar presupuesto filtrado en Excel",
        data=buffer.getvalue(),
        file_name="presupuesto_filtrado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ---------------- ALERTA POR SOBREPRESUPUESTO ----------------
st.markdown("### 🚨 Alertas por sobrepresupuesto")

# Puedes definir tus propios límites estimados aquí
presupuesto_estimado = {
    "Nómina": 50000,
    "Servicios": 15000,
    "Mantenimiento": 10000,
    "Marketing": 8000,
    "Papelería": 3000,
    "Otros": 5000
}

categorias_alerta = []

for cat in filtered_df["Categoría"].unique():
    gasto = filtered_df[filtered_df["Categoría"] == cat]["Total c/IVA"].sum()
    limite = presupuesto_estimado.get(cat, None)

    if limite and gasto > limite:
        categorias_alerta.append((cat, gasto, limite))

if categorias_alerta:
    for cat, gasto, limite in categorias_alerta:
        st.error(f"🔴 ¡Atención! La categoría **{cat}** ha excedido su límite. Gastado: ${gasto:,.2f} / Límite: ${limite:,.2f}")
else:
    st.success("✅ Todas las categorías están dentro del presupuesto estimado.")


# ---------------- TAB 2: HISTORIAL ----------------
with tab2:
    st.header("📁 Historial de Conceptos Guardados")
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet_hist = client.open_by_key("1AL2lrmiaCg77ZTLBOrwEctUhwjT1iZ60AferLPDoQYQ").worksheet("Histórico_diario")
        data_hist = sheet_hist.get_all_records()
        df_hist = pd.DataFrame(data_hist)

        if not df_hist.empty:
            col1, col2 = st.columns(2)
            with col1:
                year_hist = st.selectbox("Filtrar por Año", sorted(df_hist["Año"].unique()), key="hist_anio")
            with col2:
                categorias = df_hist["Categoría"].unique().tolist()
                categoria_hist = st.multiselect("Filtrar por Categoría", categorias, default=categorias, key="hist_cat")

            df_filtrado = df_hist[(df_hist["Año"] == year_hist) & (df_hist["Categoría"].isin(categoria_hist))]
            st.dataframe(df_filtrado, use_container_width=True)

            fig_hist = px.bar(df_filtrado, x="Categoría", y="Total c/IVA", color="Categoría", title="Totales por Categoría en el Historial")
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("⚠️ Aún no hay datos en el historial.")

    except Exception as e:
        st.error(f"❌ Error al cargar el historial: {e}")

# ---------------- BOTÓN PARA EXPORTAR A PDF ----------------
st.markdown("""
    <br>
    <button onclick="window.print()" style="
        padding: 10px 20px;
        font-size: 16px;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    ">🖨️ Exportar Dashboard como PDF</button>
""", unsafe_allow_html=True)


from datetime import datetime, timedelta

# Detectar fechas de pago próximas
hoy = datetime.today().date()
proximos_dias = hoy + timedelta(days=5)

if "Fecha de Pago" in df.columns:
    df["Fecha de Pago"] = pd.to_datetime(df["Fecha de Pago"], errors='coerce').dt.date
    alertas = df[df["Fecha de Pago"].between(hoy, proximos_dias)]

    if not alertas.empty:
        st.warning("🔔 Hay conceptos con fecha de pago cercana:")
        for i, row in alertas.iterrows():
            st.write(f"➡️ **{row['Concepto']}** de la categoría *{row['Categoría']}* vence el **{row['Fecha de Pago']}** por **${row['Monto']:.2f}**.")

