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

# Eliminar registros cuyo nombre contenga cualquiera de estas palabras
df = df[~df["Nombre"].str.lower().str.contains('|'.join(tiendas_no_restaurantes))].reset_index(drop=True)

# ✅ Recalcular el puntaje
df["Puntaje"] = df["Calificación"] * np.log1p(df["Número de Opiniones"])
df["Puntaje Normalizado"] = 5 * (df["Puntaje"] - df["Puntaje"].min()) / (df["Puntaje"].max() - df["Puntaje"].min())

# ✅ Definir el Top 15 y Top 100 actualizado
top_15_restaurantes = df.nlargest(15, "Puntaje Normalizado").reset_index(drop=True)
top_100_restaurantes = df.nlargest(100, "Puntaje Normalizado").reset_index(drop=True)

print(f"✅ Dataset limpio con {len(df)} registros.")
print(f"✅ Top 15 calculado con {len(top_15_restaurantes)} registros.")
print(f"✅ Top 100 calculado con {len(top_100_restaurantes)} registros.")


# ✅ Configuración del Dashboard
st.set_page_config(page_title="Dashboard Restaurantes Tijuana", layout="wide")
st.title("📊 Dashboard de Restaurantes en UberEats - Tijuana")

# ----------------------------------------------------------------------------------------
# 🔹 Gráfico 1: Top 10 Restaurantes Mejor Calificados
st.header("🏆 Top 10 Restaurantes Mejor Calificados")

st.markdown("""
Este gráfico muestra los **10 restaurantes mejor calificados** en Tijuana según un puntaje ponderado que toma en cuenta tanto la calificación como el número de opiniones.
""")

# 🔹 Filtrar solo el Top 10
top_10_restaurantes = top_15_restaurantes.nlargest(10, "Puntaje Normalizado")

# 🔹 Reducción del tamaño del gráfico
fig1, ax1 = plt.subplots(figsize=(3, 1.5))  # Tamaño súper reducido

# 🔹 Estilo del gráfico
colors = sns.color_palette("Blues", n_colors=10)
sns.barplot(
    data=top_10_restaurantes.sort_values(by="Puntaje Normalizado"),
    x="Nombre",
    y="Puntaje Normalizado",
    palette=colors,
    ax=ax1,
    alpha=0.9
)

# 🔹 Agregar los valores encima de las barras
for i, valor in enumerate(top_10_restaurantes.sort_values(by="Puntaje Normalizado")["Puntaje Normalizado"]):
    ax1.text(i, valor + 0.02, f"{valor:.2f}", ha='center', va='bottom', fontsize=5, color='white')

# 🔹 Ajustar títulos y etiquetas
ax1.set_title("Top 10 Restaurantes Mejor Calificados", fontsize=7, fontweight="bold", color="white")
ax1.set_xlabel("")
ax1.set_ylabel("Puntaje Normalizado (0 a 5)", fontsize=6, color="white")

# 🔹 Ajustar etiquetas del eje X para evitar solapamiento
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=35, ha="right", fontsize=5, color="white")

# 🔹 Fondo oscuro y ajuste de líneas de referencia
ax1.set_facecolor("#222222")
fig1.patch.set_facecolor("#222222")
ax1.tick_params(axis='y', labelsize=5, colors='white')
ax1.grid(axis='y', linestyle='--', alpha=0.3, color='gray')

# 🔹 Mostrar en Streamlit
st.pyplot(fig1)




# ----------------------------------------------------------------------------------------
# 🔹 Gráfico 2: Histograma de Calificaciones
st.header("📊 Distribución de Calificaciones")

st.markdown("""
Aquí se visualiza la **frecuencia de las calificaciones** de los restaurantes, lo que permite entender cómo se distribuyen las valoraciones dentro de la ciudad.
""")

fig2, ax2 = plt.subplots(figsize=(8, 6))
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

fig3, ax3 = plt.subplots(figsize=(7, 5))
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
