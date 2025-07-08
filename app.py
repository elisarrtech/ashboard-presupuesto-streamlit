import streamlit as st
import pandas as pd

# Cargar archivo Excel
uploaded_file = st.file_uploader("Carga tu archivo Excel", type=["xlsx", "xls"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # Normalizar nombres de columnas (opcional)
    df.columns = [col.strip().upper() for col in df.columns]
    
    st.title("Dashboard de Presupuesto")
    st.markdown("### Vista General de la Tabla")

    # Filtros
    col1, col2, col3, col4 = st.columns(4)
    meses = ['Todos'] + sorted(df['MES'].unique())
    categorias = ['Todas'] + sorted(df['CATEGORIA'].unique())
    status_options = ['Todos'] + sorted(df['STATUS'].unique())
    
    mes_sel = col1.selectbox("Mes", meses)
    cat_sel = col2.selectbox("Categoría", categorias)
    status_sel = col3.selectbox("Status", status_options)
    buscar = col4.text_input("Buscar concepto...")

    filtered_df = df.copy()
    if mes_sel != 'Todos':
        filtered_df = filtered_df[filtered_df['MES'] == mes_sel]
    if cat_sel != 'Todas':
        filtered_df = filtered_df[filtered_df['CATEGORIA'] == cat_sel]
    if status_sel != 'Todos':
        filtered_df = filtered_df[filtered_df['STATUS'] == status_sel]
    if buscar:
        filtered_df = filtered_df[filtered_df['CONCEPTO'].str.contains(buscar, case=False, na=False)]
    
    st.dataframe(filtered_df, use_container_width=True)

    # KPIs
    st.markdown("### Indicadores Clave")
    total_pagado = df[df['STATUS'] == 'PAGADO']['MONTO'].sum()
    total_no_pagado = df[df['STATUS'] == 'NO PAGADO']['MONTO'].sum()
    total_deuda = df[df['MONTO'] < 0]['MONTO'].sum()
    total = df['MONTO'].sum()

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Pagado", f"${total_pagado:,.2f}")
    kpi2.metric("Total NO Pagado", f"${total_no_pagado:,.2f}")
    kpi3.metric("Deuda Acumulada", f"${total_deuda:,.2f}")
    kpi4.metric("Total General", f"${total:,.2f}")

    # Gráficas
    import plotly.express as px
    st.markdown("### Distribución de Gastos por Categoría")
    cat_fig = px.bar(
        df.groupby('CATEGORIA')['MONTO'].sum().reset_index(),
        x='CATEGORIA', y='MONTO', color='CATEGORIA', title="Gasto por Categoría"
    )
    st.plotly_chart(cat_fig, use_container_width=True)

    st.markdown("### Evolución Mensual")
    mes_fig = px.line(
        df.groupby('MES')['MONTO'].sum().reset_index(),
        x='MES', y='MONTO', markers=True, title="Evolución de Monto Mensual"
    )
    st.plotly_chart(mes_fig, use_container_width=True)

    st.markdown("### Detalles de Deudas Pendientes")
    st.dataframe(df[(df['MONTO'] < 0) | (df['STATUS'] == 'NO PAGADO')], use_container_width=True)
else:
    st.info("Por favor, sube tu archivo de Excel para comenzar.")
