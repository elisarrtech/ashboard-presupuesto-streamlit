# utils/data_processor.py
from calendar import month_name

def clean_and_validate_data(df):
    def clean_and_validate_data(df):
    required_columns = ["Fecha de Pago", "Banco", "Concepto", "Monto", "Status"]
    
    # Si las columnas no coinciden exactamente, intenta hacer una limpieza
    df.columns = df.columns.str.strip()  # Elimina espacios extra
    current_cols = list(df.columns)
    
    if len(required_columns) != len(current_cols):
        raise ValueError(f"Número incorrecto de columnas. Esperado: {required_columns}, Recibido: {current_cols}")

    if not all([rc in current_cols for rc in required_columns]):
        missing = [col for col in required_columns if col not in current_cols]
        raise ValueError(f"Faltan las siguientes columnas requeridas: {', '.join(missing)}. Recibido: {current_cols}")
        
    # Renombramos (opcional si ya están bien)
    df = df.rename(columns={"Fecha de Pago": "Fecha", "Banco": "Categoría"})
    
    # Continúa con el resto del procesamiento
    from calendar import month_name
    meses_es = {i: month_name[i] for i in range(1, 13)}
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Mes"] = df["Fecha"].dt.month.map(meses_es)

    return df
