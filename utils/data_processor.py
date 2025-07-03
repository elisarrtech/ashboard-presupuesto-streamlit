# utils/data_processor.py
from calendar import month_name

def clean_and_validate_data(df):
    required_columns = ["Fecha de Pago", "Banco", "Concepto", "Monto", "Status"]
    if not all(col in df.columns for col in required_columns):
        missing = [col for col in required_columns if col not in df.columns]
        raise ValueError(f"Faltan las siguientes columnas requeridas: {', '.join(missing)}")

    meses_es = {i: month_name[i] for i in range(1, 13)}
    df.columns = df.columns.str.strip()
    df = df.rename(columns={"Fecha de Pago": "Fecha", "Banco": "Categoría"})
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Mes"] = df["Fecha"].dt.month.map(meses_es)

    return df
