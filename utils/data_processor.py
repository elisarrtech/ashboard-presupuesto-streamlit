import pandas as pd
from calendar import month_name
from io import BytesIO

def clean_and_validate_data(df):
    required_columns = ["Mes", "Categoría", "Banco", "Concepto", "Monto", "Fecha de pago", "Status"]

    df.columns = df.columns.astype(str).str.strip()

    # Validar que las columnas requeridas estén presentes
    current_cols = list(df.columns)
    missing_cols = [col for col in required_columns if col not in current_cols]
    if missing_cols:
        raise ValueError(f"Faltan columnas requeridas: {', '.join(missing_cols)}. Columnas actuales: {current_cols}")

    # Convertir 'Fecha de pago' a datetime y 'Monto' a numérico
    df["Fecha de pago"] = pd.to_datetime(df["Fecha de pago"], errors="coerce")
    df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce")

    # Agregar columnas Mes_num y Mes en inglés
    df["Mes_num"] = df["Fecha de pago"].dt.month
    df["Mes"] = df["Mes_num"].map({i: month_name[i] for i in range(1, 13)})

    # Eliminar filas con fechas no válidas
    df = df.dropna(subset=["Fecha de pago"])

    return df

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Presupuesto")
        writer.save()
    processed_data = output.getvalue()
    return processed_data
