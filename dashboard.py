import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import os

# 📌 Cargar el dataset asegurando la ruta correcta
file_path = os.path.join(os.path.dirname(__file__), "restaurantes_ubereats_tijuana_final_v4.csv")
df = pd.read_csv(file_path)

# ✅ Limpiar la columna 'Número de Opiniones' (quitar + y ,)
df["Número de Opiniones"] = df["Número de Opiniones"].replace({r"\+": "", ",": ""}, regex=True).astype(float)

# ✅ Calcular puntaje ponderado basado en calificación y número de opiniones
df["Puntaje"] = df["Calificación"] * np.log1p(df["Número de Opiniones"])
df["Puntaje Normalizado"] = 5 * (df["Puntaje"] - df["Puntaje"].min()) / (df["Puntaje"].max() - df["Puntaje"].min())

# ✅ Seleccionar los 15 y 100 mejores restaurantes según el puntaje ponderado
top_15_restaurantes = df.nlargest(15, "Puntaje Normalizado").reset_index(drop=True)
top_100_restaurantes = df.nlargest(100, "Puntaje Normalizado")

# 📌 Agregar ranking del 1 al 15
top_15_restaurantes.insert(0, "Ranking", range(1, 16))

# 📌 Iniciar el Dashboard
st.title("📊 Dashboard de Restaurantes en UberEats - Tijuana")

# 🔹 Sección 1: Top 15 Restaurantes por Puntaje
st.header("🏆 Top 15 Restaurantes Mejor Calificados")
st.write(
    "Este gráfico muestra los **15 mejores restaurantes** en UberEats de Tijuana, "
    "ordenados según su **calificación** y **cantidad de opiniones**. "
    "El puntaje ponderado considera ambos factores para destacar los restaurantes "
    "más confiables y populares."
)

fig, ax = plt.subplots(figsize=(12, 7))
sns.barplot(
    data=top_15_restaurantes.sort_values(by="Puntaje Normalizado", ascending=False),
    x="Puntaje Normalizado",
    y="Nombre",
    palette="magma",
    hue=None,
    legend=False
)
ax.set_title("Top 15 Restaurantes por Puntaje Ponderado (Normalizado 0 a 5)")
ax.set_xlabel("Puntaje Ponderado (0 a 5)")
ax.set_ylabel("Restaurante")
st.pyplot(fig)

# 🔹 Sección 2: Histograma - Frecuencia de Calificaciones
st.header("📊 Distribución de Calificaciones")

fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(df["Calificación"], bins=20, kde=True, color="royalblue", edgecolor="black", alpha=0.7)

ax.set_title("Distribución de Calificaciones de los Restaurantes", fontsize=14, fontweight="bold")
ax.set_xlabel("Calificación", fontsize=12)
ax.set_ylabel("Frecuencia", fontsize=12)
ax.grid(axis="y", linestyle="--", alpha=0.7)

st.pyplot(fig)


# 🔹 Sección 3: Mapa de Calor de Restaurantes en Tijuana
st.header("📍 Mapa de Calor de Restaurantes en Tijuana")
st.write(
    "El mapa de calor muestra la **distribución geográfica** de los restaurantes en Tijuana. "
    "Las zonas con más restaurantes aparecerán más resaltadas, mientras que las menos densas "
    "tendrán colores más suaves."
)

# 📍 Crear el mapa centrado en Tijuana con un zoom adecuado
m = folium.Map(location=[32.5149, -117.0382], zoom_start=12)

# Filtrar coordenadas dentro del área de Tijuana
df_tijuana = df[
    (df["Latitud"] >= 32.41) & (df["Latitud"] <= 32.63) &
    (df["Longitud"] >= -117.17) & (df["Longitud"] <= -116.86)
]

# ✅ Agregar HeatMap solo si hay coordenadas
if not df_tijuana.empty:
    heat_data = df_tijuana[["Latitud", "Longitud"]].values.tolist()
    HeatMap(heat_data, radius=12, blur=15, max_zoom=1).add_to(m)
    st_folium(m, width=700, height=500)  # Ajusta tamaño del mapa
else:
    st.warning("⚠️ No se encontraron coordenadas dentro de Tijuana.")

# 🔹 Mostrar el Dataset Filtrado con ranking del 1 al 15
st.header("📋 Datos de Restaurantes Filtrados")
st.write(
    "La siguiente tabla muestra los **15 mejores restaurantes** con sus calificaciones, "
    "número de opiniones y puntaje normalizado."
)
st.dataframe(top_15_restaurantes[["Ranking", "Nombre", "Número de Opiniones", "Calificación", "Puntaje Normalizado"]])
