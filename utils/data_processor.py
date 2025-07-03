# utils/data_processor.py
from calendar import month_name

def clean_and_validate_data(df):
    required_columns = ["Fecha de Pago", "Banco", "Concepto", "Monto", "Status"]

    # Aseguramos que los nombres de las columnas sean strings y sin espacios extra
    df.columns = df.columns.astype(str).str.strip()
    current_cols = list(df.columns)

    if not all([rc in current_cols for rc in required_columns]):
        missing = [col for col in required_columns if col not in current_cols]
        raise ValueError(f"Faltan las siguientes columnas requeridas: {', '.join(missing)}. Recibido: {current_cols}")

    df = df.rename(columns={"Fecha de Pago": "Fecha", "Banco": "Categoría"})
    meses_es = {i: month_name[i] for i in range(1, 13)}
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Mes"] = df["Fecha"].dt.month.map(meses_es)

    return df
