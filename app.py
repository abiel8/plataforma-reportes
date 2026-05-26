import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard de Ventas",
    layout="wide"
)

st.title("Plataforma de Reportes y Análisis de Datos")

archivo = st.file_uploader(
    "Sube un archivo Excel o CSV",
    type=["csv","xlsx"]
)

if archivo:

    if archivo.name.endswith(".csv"):
        datos = pd.read_csv(archivo)
    else:
        datos = pd.read_excel(archivo)

    st.subheader("Datos cargados")

    st.dataframe(datos)

    total_ventas = datos["Total"].sum()

    productos = datos["Producto"].nunique()

    categorias = datos["Categoria"].nunique()

    col1,col2,col3 = st.columns(3)

    col1.metric(
        "Ventas Totales",
        f"${total_ventas:,.2f}"
    )

    col2.metric(
        "Productos",
        productos
    )

    col3.metric(
        "Categorías",
        categorias
    )

    ventas_categoria = (
        datos
        .groupby("Categoria")["Total"]
        .sum()
        .reset_index()
    )

    grafico = px.bar(
        ventas_categoria,
        x="Categoria",
        y="Total",
        title="Ventas por Categoría"
    )

    st.plotly_chart(
        grafico,
        use_container_width=True
    )