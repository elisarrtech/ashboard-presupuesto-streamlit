import pandas as pd
from calendar import month_name

def clean_and_validate_data(df):
    required_columns = ["Fecha", "Categoría", "Concepto", "Monto", "Status"]

    # Eliminar espacios y asegurar que todas las columnas tengan nombre
    df.columns = df.columns.astype(str).str.strip()

    # Validar que las columnas requeridas estén presentes
    current_cols = list(df.columns)
    missing_cols = [col for col in required_columns if col not in current_cols]
    if missing_cols:
        raise ValueError(f"Faltan las siguientes columnas requeridas: {', '.join(missing_cols)}. Encontradas: {current_cols}")

    # Asegurar tipos de datos
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce")

    # Agregar columnas de mes
    df["Mes_num"] = df["Fecha"].dt.month
    df["Mes"] = df["Mes_num"].map({i: month_name[i] for i in range(1, 13)})

    # Eliminar filas con fechas no válidas
    df = df.dropna(subset=["Fecha"])

    return df

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")
