# components/sidebar.py
import streamlit as st
from datetime import datetime
from calendar import month_name
import pandas as pd

def render_sidebar(df, sheet):
    st.sidebar.header("➕ Agregar / ✏️ Editar Concepto")
    modo = st.sidebar.radio("Modo", ["Agregar", "Editar"])

    meses_es = {i: month_name[i] for i in range(1, 13)}

    if modo == "Agregar":
        with st.sidebar.form("Agregar Concepto"):
            fecha = st.date_input("Fecha", value=datetime.today())
            categoria = st.text_input("Categoría")
            concepto = st.text_input("Concepto")
            monto = st.number_input("Monto", min_value=0.0)
            status = st.selectbox("Status", ["PAGADO", "PENDIENTE"])
            submit = st.form_submit_button("Guardar")

        if submit:
            nuevo = pd.DataFrame([{
                "Fecha": fecha,
                "Categoría": categoria,
                "Concepto": concepto,
                "Monto": float(monto),
                "Status": status,
                "Mes_num": fecha.month,
                "Mes": meses_es[fecha.month]
            }])
            df = pd.concat([df, nuevo], ignore_index=True)
            from utils.data_loader import save_gsheet_data
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
            df.at[fila, "Monto"] = float(monto)
            df.at[fila, "Status"] = status
            df.at[fila, "Mes_num"] = fecha.month
            df.at[fila, "Mes"] = meses_es[fecha.month]
            from utils.data_loader import save_gsheet_data
            save_gsheet_data(sheet, df)
            st.success("✅ Concepto actualizado correctamente.")
