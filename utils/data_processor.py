# utils/data_processor.py
import streamlit as st  # ✅ Importación añadida aquí
import pandas as pd
from calendar import month_name

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def clean_and_validate_data(df):
    required_columns = ["Fecha", "Categoría", "Concepto", "Monto", "Status"]

    df.columns = df.columns.astype(str).str.strip()
    current_cols = list(df.columns)

    if not all([rc in current_cols for rc in required_columns]):
        missing = [col for col in required_columns if col not in current_cols]
        raise ValueError(f"Faltan las siguientes columnas requeridas: {', '.join(missing)}. Recibido: {current_cols}")

    meses_es = {i: month_name[i] for i in range(1, 13)}
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Mes"] = df["Fecha"].dt.month.map(meses_es)

    return df
