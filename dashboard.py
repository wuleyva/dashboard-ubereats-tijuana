import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import os

# 📌 Cargar datos
df = pd.read_csv("restaurantes_ubereats_tijuana_final_v4.csv")

# ✅ Conversión de tipos de datos
df["Número de Opiniones"] = pd.to_numeric(df["Número de Opiniones"], errors="coerce")
df["Calificación"] = pd.to_numeric(df["Calificación"], errors="coerce")
df["Latitud"] = pd.to_numeric(df["Latitud"], errors="coerce")
df["Longitud"] = pd.to_numeric(df["Longitud"], errors="coerce")

# ✅ Eliminar registros con datos faltantes esenciales
df.dropna(subset=["Nombre", "Categoría", "Calificación", "Número de Opiniones", "Latitud", "Longitud"], inplace=True)

# ✅ Filtrar solo coordenadas dentro de Tijuana
df = df[
    (df["Latitud"] >= 32.41) & (df["Latitud"] <= 32.63) &
    (df["Longitud"] >= -117.17) & (df["Longitud"] <= -116.86)
].reset_index(drop=True)

# ✅ Eliminar tiendas de autoservicio y no restaurantes
tiendas_no_restaurantes = [
    "oxxo", "7-eleven", "soriana", "calimax", "aprecio", "ley",
    "the home depot", "costco", "walmart", "sam's club", "chedraui", "modelorama"
]

df = df[~df["Nombre"].str.lower().str.contains('|'.join(tiendas_no_restaurantes))].reset_index(drop=True)

# ✅ Recalcular el puntaje
df["Puntaje"] = df["Calificación"] * np.log1p(df["Número de Opiniones"])
df["Puntaje Normalizado"] = 5 * (df["Puntaje"] - df["Puntaje"].min()) / (df["Puntaje"].max() - df["Puntaje"].min())

# ✅ Definir el Top 10 y Top 100 actualizado
top_10_restaurantes = df.nlargest(10, "Puntaje Normalizado").reset_index(drop=True)
top_100_restaurantes = df.nlargest(100, "Puntaje Normalizado").reset_index(drop=True)

# ✅ Configuración del Dashboard
st.set_page_config(page_title="Dashboard Restaurantes Tijuana", layout="wide")
st.title("📊 Dashboard de Restaurantes en UberEats - Tijuana")

# ----------------------------------------------------------------------------------------
# 🔹 Gráfico 1: Top 10 Restaurantes Mejor Calificados
st.header("🏆 Top 10 Restaurantes Mejor Calificados")

st.markdown("""
Este gráfico muestra los **10 restaurantes mejor calificados** en Tijuana según un puntaje ponderado que toma en cuenta tanto la calificación como el número de opiniones.
""")

# 🔹 Crear la figura con los restaurantes en el eje vertical
fig1, ax1 = plt.subplots(figsize=(2.5, 3))  # 🔽 Gráfico vertical y más compacto

# 🔹 Estilo del gráfico con marcos
colors = sns.color_palette("Blues", n_colors=10)
sns.barplot(
    data=top_10_restaurantes.sort_values(by="Puntaje Normalizado"),
    y="Nombre",
    x="Puntaje Normalizado",
    palette=colors,
    ax=ax1,
    alpha=0.9,
    edgecolor="white"  # 🔹 Bordes en cada barra
)

# 🔹 Agregar valores en cada barra
for i, valor in enumerate(top_10_restaurantes.sort_values(by="Puntaje Normalizado")["Puntaje Normalizado"]):
    ax1.text(valor + 0.05, i, f"{valor:.2f}", ha='left', va='center', fontsize=5, color='white')

# 🔹 Agregar un marco al gráfico
for spine in ax1.spines.values():
    spine.set_edgecolor('white')
    spine.set_linewidth(1.2)

# 🔹 Ajustar títulos y etiquetas
ax1.set_title("Top 10 Restaurantes Mejor Calificados", fontsize=8, fontweight="bold", color="white")
ax1.set_xlabel("Puntaje Normalizado (0 a 5)", fontsize=6, color="white")
ax1.set_ylabel("")

# 🔹 Fondo oscuro y ajuste de líneas
ax1.set_facecolor("#222222")
fig1.patch.set_facecolor("#222222")
ax1.tick_params(axis='x', labelsize=6, colors='white')
ax1.tick_params(axis='y', labelsize=6, colors='white')
ax1.grid(axis='x', linestyle='--', alpha=0.3, color='gray')

# 🔹 Mostrar en Streamlit
st.pyplot(fig1)

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
# 🔹 Gráfico 3: Dispersión de Calificación vs Opiniones
st.header("📌 Calificación vs Número de Opiniones (Top 100)")

st.markdown("""
Relación entre la **calificación** y el **número de opiniones** de los 100 mejores restaurantes, resaltando cómo las calificaciones se comportan según la popularidad.
""")

fig3, ax3 = plt.subplots(figsize=(6, 4))
scatter = ax3.scatter(
    top_100_restaurantes["Calificación"],
    top_100_restaurantes["Número de Opiniones"],
    c=top_100_restaurantes["Puntaje Normalizado"],
    cmap="Blues",
    s=80,
    edgecolor="white",
    alpha=0.9
)
cbar = plt.colorbar(scatter)
cbar.set_label("Puntaje Normalizado", color="white")
cbar.ax.yaxis.set_tick_params(color='white')
plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')

# 🔹 Agregar marco
for spine in ax3.spines.values():
    spine.set_edgecolor('white')
    spine.set_linewidth(1.2)

ax3.set_title("Top 100 Restaurantes: Calificación vs Número de Opiniones", fontsize=10, fontweight="bold", color="white")
ax3.set_xlabel("Calificación", fontsize=8, color="white")
ax3.set_ylabel("Número de Opiniones", fontsize=8, color="white")
ax3.set_facecolor("#222222")
fig3.patch.set_facecolor("#222222")
ax3.tick_params(axis='x', labelsize=6, colors='white')
ax3.tick_params(axis='y', labelsize=6, colors='white')
ax3.grid(True, linestyle='--', alpha=0.3, color='gray')

st.pyplot(fig3)

# ----------------------------------------------------------------------------------------
# ✅ Mostrar el dataset
st.header("📋 Top 10 Restaurantes")
top_10_restaurantes.index += 1
st.dataframe(top_10_restaurantes[["Nombre", "Número de Opiniones", "Calificación", "Puntaje Normalizado"]])


