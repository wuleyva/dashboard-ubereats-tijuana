import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

# ✅ Cargar dataset
df = pd.read_csv("restaurantes_ubereats_tijuana_final_v4.csv")

# ✅ Limpieza
df["Número de Opiniones"] = pd.to_numeric(df["Número de Opiniones"], errors="coerce")
df["Calificación"] = pd.to_numeric(df["Calificación"], errors="coerce")
df["Latitud"] = pd.to_numeric(df["Latitud"], errors="coerce")
df["Longitud"] = pd.to_numeric(df["Longitud"], errors="coerce")
df = df.dropna(subset=["Número de Opiniones", "Calificación", "Latitud", "Longitud"])

# ✅ Puntaje ponderado
df["Puntaje"] = df["Calificación"] * np.log1p(df["Número de Opiniones"])
df["Puntaje Normalizado"] = 5 * (df["Puntaje"] - df["Puntaje"].min()) / (df["Puntaje"].max() - df["Puntaje"].min())

# ✅ Top 15 restaurantes
top_15_restaurantes = df.nlargest(15, "Puntaje Normalizado").reset_index(drop=True)
top_15_restaurantes.index = top_15_restaurantes.index + 1

# ✅ Dashboard
st.set_page_config(layout="wide")
st.title("📊 Dashboard de Restaurantes UberEats Tijuana")

# 🔹 Descripción Gráfico de Barras
st.markdown("""
### 🏆 Top 15 Restaurantes Mejor Calificados
Este gráfico muestra los 15 mejores restaurantes de Tijuana según su puntaje ponderado, 
que combina la calificación del usuario con la cantidad de opiniones recibidas. 
Se usa una escala de tonos azules para resaltar las diferencias de puntuación.
""")

# 🔹 Gráfico de barras (Tonos Azules)
fig_bar, ax_bar = plt.subplots(figsize=(16, 8))
colors = sns.color_palette("Blues", n_colors=15)
bars = sns.barplot(
    data=top_15_restaurantes.sort_values(by="Puntaje Normalizado", ascending=True),
    x="Nombre",
    y="Puntaje Normalizado",
    palette=colors,
    ax=ax_bar
)
for i, valor in enumerate(top_15_restaurantes.sort_values(by="Puntaje Normalizado")["Puntaje Normalizado"]):
    ax_bar.text(i, valor + 0.05, f"{valor:.2f}", ha='center', va='bottom', fontsize=12, color='white')
ax_bar.set_title("Top 15 Restaurantes Mejor Calificados en Tijuana (Tonos Azules)", fontsize=20, fontweight="bold", color="white")
ax_bar.set_xlabel("")
ax_bar.set_ylabel("Puntaje Normalizado (0 a 5)", fontsize=14, color="white")
ax_bar.set_facecolor("#222222")
fig_bar.patch.set_facecolor("#222222")
ax_bar.tick_params(axis='x', rotation=45, labelsize=12, colors='white')
ax_bar.tick_params(axis='y', labelsize=12, colors='white')
ax_bar.grid(axis='y', linestyle='--', alpha=0.3, color='gray')
st.pyplot(fig_bar)

# 🔹 Descripción Histograma
st.markdown("""
### 📌 Distribución de Calificaciones
En este histograma observamos cómo se distribuyen las calificaciones de los restaurantes en Tijuana.
Nos ayuda a entender si la mayoría de los locales tienen buenas evaluaciones o si hay muchas calificaciones bajas.
""")

# 🔹 Histograma de calificaciones
fig_hist, ax_hist = plt.subplots(figsize=(12, 6))
sns.histplot(df["Calificación"], bins=20, kde=True, color="royalblue", edgecolor="white", alpha=0.9, ax=ax_hist)
ax_hist.set_title("Distribución de Calificaciones de Restaurantes", fontsize=20, color='white')
ax_hist.set_xlabel("Calificación", fontsize=14, color='white')
ax_hist.set_ylabel("Frecuencia", fontsize=14, color='white')
ax_hist.set_facecolor("#222222")
fig_hist.patch.set_facecolor("#222222")
ax_hist.tick_params(axis='x', colors='white')
ax_hist.tick_params(axis='y', colors='white')
ax_hist.grid(axis='y', linestyle='--', alpha=0.3, color='gray')
st.pyplot(fig_hist)

# 🔹 Descripción Mapa de Calor
st.markdown("""
### 📍 Mapa de Calor de Restaurantes
El mapa resalta las zonas con mayor concentración de restaurantes dentro de Tijuana.
Las áreas con colores más cálidos (rojo, naranja) indican zonas con más presencia de locales.
""")

# 🔹 Mapa de calor estilo dark
heat_data = df[["Latitud", "Longitud"]].dropna().values.tolist()
gradient_dark = {
    0.2: "blue",
    0.4: "purple",
    0.6: "orange",
    0.8: "red",
    1.0: "yellow"
}
m = folium.Map(
    location=[32.5149, -117.0382],
    zoom_start=12,
    tiles="CartoDB dark_matter"
)
if heat_data:
    HeatMap(
        heat_data,
        gradient=gradient_dark,
        radius=15,
        blur=20,
        max_zoom=1
    ).add_to(m)
    st_folium(m, width=1000, height=600)
else:
    st.warning("❌ No hay datos válidos para el mapa.")

# 🔹 Descripción de tabla
st.markdown("""
### 📋 Tabla Top 15 Restaurantes
Aquí puedes ver el detalle del Top 15 con sus respectivas calificaciones, número de opiniones y puntaje normalizado.
""")

# 🔹 Mostrar Top 15 restaurantes
st.dataframe(top_15_restaurantes[["Nombre", "Número de Opiniones", "Calificación", "Puntaje Normalizado"]].style.set_properties(**{'background-color': '#111111', 'color': 'white'}))


