import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================

st.set_page_config(
    page_title="Plataforma de Reportes",
    layout="wide"
)

st.title(" Plataforma de Reportes y Análisis de Datos")

# ==========================
# CARGA DE ARCHIVO
# ==========================

archivo = st.file_uploader(
    "Sube un archivo Excel o CSV",
    type=["csv", "xlsx"]
)

if archivo is not None:

    # ==========================
    # LEER ARCHIVO
    # ==========================

    try:

        if archivo.name.endswith(".csv"):
            datos = pd.read_csv(archivo)

        else:
            datos = pd.read_excel(archivo)

        st.success("Archivo cargado correctamente")

    except Exception as e:

        st.error(f"Error al leer el archivo: {e}")
        st.stop()

    # ==========================
    # MOSTRAR TABLA
    # ==========================

    st.subheader("Vista previa de los datos")

    st.dataframe(
        datos,
        use_container_width=True
    )

    # ==========================
    # FILTRO DE CATEGORÍA
    # ==========================

    st.sidebar.header("Filtros")

    if "Categoria" in datos.columns:

        categorias = datos["Categoria"].dropna().unique()

        categorias_seleccionadas = st.sidebar.multiselect(
            "Seleccione categorías",
            categorias,
            default=categorias
        )

        datos_filtrados = datos[
            datos["Categoria"].isin(categorias_seleccionadas)
        ]

    else:

        datos_filtrados = datos

    # ==========================
    # KPIs
    # ==========================

    st.subheader("Indicadores")

    col_numericas = datos_filtrados.select_dtypes(include="number").columns

    if len(col_numericas) > 0:

        columna_kpi = st.selectbox(
            "Seleccione la columna numérica para indicadores",
            col_numericas
        )

        total = datos_filtrados[columna_kpi].sum()

        promedio = datos_filtrados[columna_kpi].mean()

        registros = len(datos_filtrados)

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total",
            f"{total:,.2f}"
        )

        col2.metric(
            "Promedio",
            f"{promedio:,.2f}"
        )

        col3.metric(
            "Registros",
            registros
        )

    # ==========================
    # SELECCIÓN DE COLUMNAS
    # ==========================

    st.subheader("Generador de gráficos")

    columnas = datos_filtrados.columns.tolist()

    eje_x = st.selectbox(
        "Seleccione la columna para el eje X",
        columnas
    )

    columnas_numericas = datos_filtrados.select_dtypes(
        include="number"
    ).columns.tolist()

    if len(columnas_numericas) == 0:

        st.warning(
            "No existen columnas numéricas para generar gráficos."
        )

        st.stop()

    eje_y = st.selectbox(
        "Seleccione la columna para el eje Y",
        columnas_numericas
    )

    # ==========================
    # TIPO DE GRÁFICO
    # ==========================

    tipo_grafico = st.selectbox(
        "Tipo de gráfico",
        [
            "Barras",
            "Pastel",
            "Líneas",
            "Dispersión"
        ]
    )

    # ==========================
    # CREAR GRÁFICO
    # ==========================

    try:

        if tipo_grafico == "Barras":

            resumen = (
                datos_filtrados
                .groupby(eje_x)[eje_y]
                .sum()
                .reset_index()
            )

            fig = px.bar(
                resumen,
                x=eje_x,
                y=eje_y,
                title=f"{eje_y} por {eje_x}"
            )

        elif tipo_grafico == "Pastel":

            resumen = (
                datos_filtrados
                .groupby(eje_x)[eje_y]
                .sum()
                .reset_index()
            )

            fig = px.pie(
                resumen,
                names=eje_x,
                values=eje_y,
                title=f"Distribución de {eje_y}"
            )

        elif tipo_grafico == "Líneas":

            resumen = (
                datos_filtrados
                .groupby(eje_x)[eje_y]
                .sum()
                .reset_index()
            )

            fig = px.line(
                resumen,
                x=eje_x,
                y=eje_y,
                title=f"{eje_y} por {eje_x}"
            )

        else:

            fig = px.scatter(
                datos_filtrados,
                x=eje_x,
                y=eje_y,
                title=f"{eje_y} vs {eje_x}"
            )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    except Exception as e:

        st.error(
            f"No fue posible generar el gráfico: {e}"
        )

    # ==========================
    # DATOS FILTRADOS
    # ==========================

    st.subheader("Datos filtrados")

    st.dataframe(
        datos_filtrados,
        use_container_width=True
    )