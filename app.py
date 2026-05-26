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

st.title("Plataforma de Reportes y Análisis de Datos")

# ==========================
# CARGA DE ARCHIVO
# ==========================

archivo = st.file_uploader(
    "Sube un archivo Excel o CSV",
    type=["csv", "xlsx"]
)

if archivo is None:

    st.info(
        "👆 Sube un archivo Excel (.xlsx) o CSV (.csv) para comenzar.\n\n"
        "La aplicación generará automáticamente indicadores, tablas y gráficos interactivos."
    )
    st.stop()

# ==========================
# LEER ARCHIVO
# ==========================

try:

    if archivo.name.endswith(".csv"):
        datos = pd.read_csv(archivo)

    else:
        datos = pd.read_excel(archivo)

    st.success(f"✅ Archivo **{archivo.name}** cargado correctamente — {len(datos)} registros encontrados.")

except Exception as e:

    st.error(f"Error al leer el archivo: {e}")
    st.stop()

# ==========================
# FILTROS EN SIDEBAR
# ==========================

st.sidebar.header("Filtros")

datos_filtrados = datos.copy()

# Filtro por categoría
if "Categoria" in datos.columns:

    categorias = datos["Categoria"].dropna().unique()

    categorias_seleccionadas = st.sidebar.multiselect(
        "Seleccione categorías",
        categorias,
        default=categorias
    )

    datos_filtrados = datos_filtrados[
        datos_filtrados["Categoria"].isin(categorias_seleccionadas)
    ]

# Filtro por rango de fechas
col_fechas = [
    col for col in datos.columns
    if pd.api.types.is_datetime64_any_dtype(datos[col])
    or (datos[col].dtype == object and _es_fecha(datos[col]))
]

def _es_fecha(serie):
    try:
        pd.to_datetime(serie.dropna().head(10))
        return True
    except Exception:
        return False

for col in datos.columns:
    if datos[col].dtype == object:
        try:
            datos_filtrados[col] = pd.to_datetime(datos_filtrados[col])
            col_fechas.append(col)
            break
        except Exception:
            pass

col_fecha_detectada = None
for col in datos_filtrados.columns:
    if pd.api.types.is_datetime64_any_dtype(datos_filtrados[col]):
        col_fecha_detectada = col
        break

if col_fecha_detectada:

    fecha_min = datos_filtrados[col_fecha_detectada].min().date()
    fecha_max = datos_filtrados[col_fecha_detectada].max().date()

    rango = st.sidebar.date_input(
        f"Rango de fechas ({col_fecha_detectada})",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max
    )

    if isinstance(rango, (list, tuple)) and len(rango) == 2:
        fecha_inicio, fecha_fin = rango
        datos_filtrados = datos_filtrados[
            (datos_filtrados[col_fecha_detectada].dt.date >= fecha_inicio) &
            (datos_filtrados[col_fecha_detectada].dt.date <= fecha_fin)
        ]

# ==========================
# MOSTRAR TABLA
# ==========================

st.subheader("Vista previa de los datos")

st.dataframe(
    datos_filtrados,
    use_container_width=True
)

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

    total    = datos_filtrados[columna_kpi].sum()
    promedio = datos_filtrados[columna_kpi].mean()
    minimo   = datos_filtrados[columna_kpi].min()
    maximo   = datos_filtrados[columna_kpi].max()
    registros = len(datos_filtrados)

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total",     f"{total:,.2f}")
    col2.metric("Promedio",  f"{promedio:,.2f}")
    col3.metric("Mínimo",    f"{minimo:,.2f}")
    col4.metric("Máximo",    f"{maximo:,.2f}")
    col5.metric("Registros", registros)

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

    st.warning("No existen columnas numéricas para generar gráficos.")
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
    ["Barras", "Pastel", "Líneas", "Dispersión"]
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

    st.error(f"No fue posible generar el gráfico: {e}")

# ==========================
# DATOS FILTRADOS + DESCARGA
# ==========================

st.subheader("Datos filtrados")

st.dataframe(
    datos_filtrados,
    use_container_width=True
)

csv_export = datos_filtrados.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Descargar datos filtrados como CSV",
    data=csv_export,
    file_name="datos_filtrados.csv",
    mime="text/csv"
)
