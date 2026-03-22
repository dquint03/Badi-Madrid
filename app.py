import streamlit as st
import pandas as pd
import plotly.express as px

# CONFIG
st.set_page_config(page_title="Dashboard Badi Madrid", layout="wide")

st.title("🏠 Dashboard alquiler habitaciones Madrid")

# CARGAR DATOS
df = pd.read_excel("badi_con_barrios.xlsx")

# -------------------------
# 🎛️ FILTROS
# -------------------------
st.sidebar.header("🔎 Filtros")

barrio = st.sidebar.selectbox(
    "Barrio",
    ["Todos"] + list(df["barrio"].dropna().unique())
)

tipo = st.sidebar.selectbox(
    "Tipo habitación",
    ["Todos"] + list(df["tipo_habitacion"].dropna().unique())
)

precio_range = st.sidebar.slider(
    "Rango de precio (€)",
    int(df["precio"].min()),
    int(df["precio"].max()),
    (int(df["precio"].min()), int(df["precio"].max()))
)

companeros = st.sidebar.slider(
    "Número de compañeros",
    int(df["# de compañeros"].min()),
    int(df["# de compañeros"].max()),
    (int(df["# de compañeros"].min()), int(df["# de compañeros"].max()))
)

# -------------------------
# 🔄 FILTRADO
# -------------------------
df_filtrado = df.copy()

if barrio != "Todos":
    df_filtrado = df_filtrado[df_filtrado["barrio"] == barrio]

if tipo != "Todos":
    df_filtrado = df_filtrado[df_filtrado["tipo_habitacion"] == tipo]

df_filtrado = df_filtrado[
    (df_filtrado["precio"] >= precio_range[0]) &
    (df_filtrado["precio"] <= precio_range[1])
]

df_filtrado = df_filtrado[
    (df_filtrado["# de compañeros"] >= companeros[0]) &
    (df_filtrado["# de compañeros"] <= companeros[1])
]

# -------------------------
# 📊 KPIs
# -------------------------
col1, col2, col3 = st.columns(3)

col1.metric("💰 Precio medio", round(df_filtrado["precio"].mean(), 2))
col2.metric("📉 Precio mínimo", df_filtrado["precio"].min())
col3.metric("📈 Precio máximo", df_filtrado["precio"].max())

st.markdown("---")

# -------------------------
# 📊 HISTOGRAMA (PLOTLY)
# -------------------------
st.subheader("📊 Distribución de precios")

fig1 = px.histogram(
    df_filtrado,
    x="precio",
    nbins=15,
    title="Distribución de precios",
    text_auto=True  # 👈 esto añade los números
)

fig1.update_traces(textposition="outside")  # 👈 los pone arriba

st.plotly_chart(fig1, use_container_width=True)

# -------------------------
# 📍 PRECIO POR BARRIO
# -------------------------
st.subheader("📍 Precio medio por barrio")

precio_barrio = df_filtrado.groupby("barrio").agg(
    precio_medio=("precio", "mean"),
    conteo=("precio", "count")
).reset_index()

fig2 = px.bar(
    precio_barrio,
    x="barrio",
    y="precio_medio",
    text="conteo",  # 👈 esto añade el número
    title="Precio medio por barrio",
)

fig2.update_traces(textposition="outside")  # 👈 coloca el número arriba

st.plotly_chart(fig2, use_container_width=True)

# -------------------------
# 🛏️ PRECIO VS COMPAÑEROS
# -------------------------
st.subheader("👥 Relación precio vs compañeros")

fig3 = px.scatter(
    df_filtrado,
    x="# de compañeros",
    y="precio",
    color="barrio",
    title="Precio vs número de compañeros",
)

st.plotly_chart(fig3, use_container_width=True)

# -------------------------
# 🧠 TOP BARRIOS CAROS
# -------------------------
st.subheader("🔥 Barrios más caros")

top_barrios = df_filtrado.groupby("barrio").agg(
    precio_medio=("precio", "mean"),
    conteo=("precio", "count")
).sort_values(by="precio_medio", ascending=False).head(10)

fig4 = px.bar(
    top_barrios,
    y="precio_medio",
    text="conteo",  # 👈 conteo arriba
    title="Top barrios más caros"
)

fig4.update_traces(textposition="outside")

st.plotly_chart(fig4, use_container_width=True)

# -------------------------
# 📋 TABLA
# -------------------------
st.subheader("📋 Datos filtrados")

st.dataframe(df_filtrado)

# -------------------------
# 🌟 TOP 5 MEJORES OPORTUNIDADES (calidad de vida)
# -------------------------
st.subheader("🌟 Top 5 oportunidades (menos compañeros + mejor precio)")

# Distritos objetivo
distritos_top = ["Salamanca", "Chamberí", "Retiro", "Chamartín", "Moncloa-Aravaca", "Centro"]

# Filtrar
df_top = df_filtrado[df_filtrado["barrio"].isin(distritos_top)].copy()

# Ordenar: menos compañeros + menor precio
df_top = df_top.sort_values(
    by=["# de compañeros", "precio"],
    ascending=[True, True]
)

# Top 5
df_top5 = df_top.head(5).copy().reset_index(drop=True)

# Ranking visual
ranking = []
for i in range(len(df_top5)):
    if i == 0:
        ranking.append("🥇 1")
    elif i == 1:
        ranking.append("🥈 2")
    elif i == 2:
        ranking.append("🥉 3")
    else:
        ranking.append(f"{i+1}")

df_top5["🏆 Ranking"] = ranking

# Seleccionar columnas (incluyendo link)
df_top5 = df_top5[[
    "🏆 Ranking",
    "barrio",
    "# de compañeros",
    "precio",
    "link"
]]

# Renombrar columnas
df_top5.columns = [
    "🏆 Ranking",
    "📍 Distrito",
    "👥 Nº compañeros",
    "💰 Precio (€)",
    "🔗 Link"
]

# Convertir link a hipervínculo bonito
df_top5["🔗 Link"] = df_top5["🔗 Link"].apply(
    lambda x: f'<a href="{x}" target="_blank">Ver anuncio</a>'
)

# Mostrar tabla con HTML (para que funcione el link)
st.markdown(
    df_top5.to_html(escape=False, index=False),
    unsafe_allow_html=True
)