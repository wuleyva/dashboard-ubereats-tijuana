import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import os

# ✅ Cargar el dataset
df = pd.read_csv("restaurantes_ubereats_tijuana_final_v4.csv")

# ✅ Limpiar columnas necesarias
df["Número de Opiniones"] = pd.to_numeric(df["Número de Opiniones"], errors="coerce")
df["Calificación"] = pd.to_numeric(df["Calificación"], errors="coerce")
df["Latitud"] = pd.to_numeric(df["Latitud"], errors="coerce")
df["Longitud"] = pd.to_numeric(df["Longitud"], errors="coerce")
df = df.dropna(subset=["Número de Opiniones", "Calificación", "Latitud", "Longitud"])

# ✅ Calcular puntaje ponderado
df["Puntaje"] = df["Calificación"] * np.log1p(df["Número de Opiniones"])
df["Puntaje Normalizado"] = 5 * (df["Puntaje"] - df["Puntaje"].min()) / (df["Puntaje"].max() - df["Puntaje"].min())

# ✅ Selección de top restaurantes
top_15_restaurantes = df.nlargest(15, "Puntaje Normalizado")
top_100_restaurantes = df.nlargest(100, "Puntaje Normalizado")

# ✅ Configuración del Dashboard
st.set_page_config(page_title="Dashboard Restaurantes Tijuana", layout="wide")
st.title("📊 Dashboard de Restaurantes en UberEats - Tijuana")

# ----------------------------------------------------------------------------------------
# 🔹 Gráfico 1: Top 15 Restaurantes Mejor Calificados
st.header("🏆 Top 15 Restaurantes Mejor Calificados")

st.markdown("""
Este gráfico muestra los **15 restaurantes mejor calificados** en Tijuana según un puntaje ponderado que toma en cuenta tanto la calificación como el número de opiniones.
""")

fig1, ax1 = plt.subplots(figsize=(16, 8))
colors = sns.color_palette("Blues", n_colors=15)
sns.barplot(
    data=top_15_restaurantes.sort_values(by="Puntaje Normalizado"),
    x="Nombre",
    y="Puntaje Normalizado",
    palette=colors,
    ax=ax1,
    alpha=0.9
)

for i, valor in enumerate(top_15_restaurantes.sort_values(by="Puntaje Normalizado")["Puntaje Normalizado"]):
    ax1.text(i, valor + 0.05, f"{valor:.2f}", ha='center', va='bottom', fontsize=12, color='white')

ax1.set_title("Top 15 Restaurantes Mejor Calificados en Tijuana (Tonos Azules)", fontsize=20, fontweight="bold", color="white")
ax1.set_xlabel("")
ax1.set_ylabel("Puntaje Normalizado (0 a 5)", fontsize=14, color="white")
ax1.set_facecolor("#222222")
fig1.patch.set_facecolor("#222222")
ax1.tick_params(axis='x', rotation=45, labelsize=12, colors='white')
ax1.tick_params(axis='y', labelsize=12, colors='white')
ax1.grid(axis='y', linestyle='--', alpha=0.3, color='gray')
st.pyplot(fig1)

# ----------------------------------------------------------------------------------------
# 🔹 Gráfico 2: Histograma de Calificaciones
st.header("📊 Distribución de Calificaciones")

st.markdown("""
Aquí se visualiza la **frecuencia de las calificaciones** de los restaurantes, lo que permite entender cómo se distribuyen las valoraciones dentro de la ciudad.
""")

fig2, ax2 = plt.subplots(figsize=(16, 8))
sns.histplot(df["Calificación"], bins=20, kde=True, color="#1f77b4", edgecolor="white", alpha=0.8)
ax2.set_title("Distribución de Calificaciones de Restaurantes", fontsize=20, fontweight="bold", color="white")
ax2.set_xlabel("Calificación", fontsize=14, color="white")
ax2.set_ylabel("Frecuencia", fontsize=14, color="white")
ax2.set_facecolor("#222222")
fig2.patch.set_facecolor("#222222")
ax2.tick_params(axis='x', labelsize=12, colors='white')
ax2.tick_params(axis='y', labelsize=12, colors='white')
ax2.grid(axis='y', linestyle='--', alpha=0.3, color='gray')
st.pyplot(fig2)

# ----------------------------------------------------------------------------------------
# 🔹 Gráfico 3: Dispersión de Calificación vs Opiniones
st.header("📌 Calificación vs Número de Opiniones (Top 100)")

st.markdown("""
Relación entre la **calificación** y el **número de opiniones** de los 100 mejores restaurantes, resaltando cómo las calificaciones se comportan según la popularidad.
""")

fig3, ax3 = plt.subplots(figsize=(14, 8))
scatter = ax3.scatter(
    top_100_restaurantes["Calificación"],
    top_100_restaurantes["Número de Opiniones"],
    c=top_100_restaurantes["Puntaje Normalizado"],
    cmap="Blues",
    s=100,
    edgecolor="white",
    alpha=0.9
)
cbar = plt.colorbar(scatter)
cbar.set_label("Puntaje Normalizado", color="white")
cbar.ax.yaxis.set_tick_params(color='white')
plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
ax3.set_title("Top 100 Restaurantes: Calificación vs Número de Opiniones", fontsize=20, fontweight="bold", color="white")
ax3.set_xlabel("Calificación", fontsize=14, color="white")
ax3.set_ylabel("Número de Opiniones", fontsize=14, color="white")
ax3.set_facecolor("#222222")
fig3.patch.set_facecolor("#222222")
ax3.tick_params(axis='x', labelsize=12, colors='white')
ax3.tick_params(axis='y', labelsize=12, colors='white')
ax3.grid(True, linestyle='--', alpha=0.3, color='gray')
st.pyplot(fig3)

# ----------------------------------------------------------------------------------------
# 🔹 Mapa de Calor
st.header("📍 Mapa de Calor de Restaurantes en Tijuana")

st.markdown("""
Mapa de calor que muestra las zonas con mayor concentración de restaurantes según su ubicación geográfica.
""")

gradient = {
    0.0: '#0000FF',
    0.4: '#4B0082',
    0.6: '#FF8C00',
    0.8: '#FF0000',
    1.0: '#FFFF00'
}

m = folium.Map(location=[32.5149, -117.0382], zoom_start=12, tiles="CartoDB dark_matter")
heat_data = df[["Latitud", "Longitud"]].values.tolist()
HeatMap(heat_data, gradient=gradient, radius=15, blur=20).add_to(m)
st_folium(m, width=1000, height=600)

# ----------------------------------------------------------------------------------------
# ✅ Mostrar el dataset
st.header("📋 Top 15 Restaurantes")
top_15_restaurantes = top_15_restaurantes.reset_index(drop=True)
top_15_restaurantes.index += 1
st.dataframe(top_15_restaurantes[["Nombre", "Número de Opiniones", "Calificación", "Puntaje Normalizado"]])

# ✅ Mensaje final
st.success("✅ Dashboard cargado exitosamente.")
