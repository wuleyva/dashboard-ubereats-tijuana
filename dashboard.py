import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium


# ✅ Cargar el dataset
df = pd.read_csv("restaurantes_ubereats_tijuana_final_v4.csv")

# ✅ Procesar los datos
df["Número de Opiniones"] = df["Número de Opiniones"].replace({r"\+": "", ",": ""}, regex=True).astype(float)
df["Puntaje"] = df["Calificación"] * np.log1p(df["Número de Opiniones"])
df["Puntaje Normalizado"] = 5 * (df["Puntaje"] - df["Puntaje"].min()) / (df["Puntaje"].max() - df["Puntaje"].min())


# ✅ Configuración general
st.set_page_config(page_title="Dashboard Restaurantes UberEats Tijuana", layout="wide")
plt.style.use("dark_background")

# ✅ Dataset (asegúrate que ya esté cargado previamente como df)
# df = pd.read_csv("restaurantes_ubereats_tijuana_final_v4.csv")

# ✅ TOP 15 y TOP 100
top_15_restaurantes = df.nlargest(15, "Puntaje Normalizado")
top_100_restaurantes = df.nlargest(100, "Puntaje Normalizado")

# Título principal
st.title("📊 Dashboard de Restaurantes en UberEats - Tijuana")

# =====================================================================================
# 🔹 1️⃣ Gráfico de Barras - Top 15 Restaurantes con efecto degradado azul
st.header("🏆 Top 15 Restaurantes Mejor Calificados")
st.markdown("Visualización del ranking de los 15 mejores restaurantes según el puntaje normalizado, con un efecto degradado en tonos azules.")

fig, ax = plt.subplots(figsize=(16, 8))
colors = sns.color_palette("Blues", n_colors=15)
bars = sns.barplot(
    data=top_15_restaurantes.sort_values(by="Puntaje Normalizado", ascending=True),
    x="Nombre",
    y="Puntaje Normalizado",
    palette=colors,
    ax=ax
)

for i, valor in enumerate(top_15_restaurantes.sort_values(by="Puntaje Normalizado", ascending=True)["Puntaje Normalizado"]):
    ax.text(i, valor + 0.05, f"{valor:.2f}", ha='center', va='bottom', fontsize=12, color='white')

ax.set_title("Top 15 Restaurantes Mejor Calificados en Tijuana (Tonos Azules)", fontsize=20, fontweight="bold")
ax.set_xlabel("")
ax.set_ylabel("Puntaje Normalizado (0 a 5)", fontsize=14)
ax.set_facecolor("#222222")
fig.patch.set_facecolor("#222222")
ax.tick_params(axis='x', rotation=45, labelsize=12)
ax.tick_params(axis='y', labelsize=12)
ax.grid(axis='y', linestyle='--', alpha=0.3)

st.pyplot(fig)

# =====================================================================================
# 🔹 2️⃣ Histograma de Frecuencia - Calificación de Restaurantes
st.header("📊 Distribución de Calificaciones de Restaurantes")
st.markdown("Este histograma muestra la frecuencia de calificaciones otorgadas a los restaurantes, con un suave degradado en tonos azules y efecto transparente.")

fig, ax = plt.subplots(figsize=(16, 8))
sns.histplot(
    data=df,
    x="Calificación",
    bins=20,
    kde=True,
    color="#1f77b4",
    edgecolor="white",
    alpha=0.7
)
ax.set_title("Distribución de Calificaciones de Restaurantes", fontsize=20, fontweight="bold")
ax.set_xlabel("Calificación", fontsize=14)
ax.set_ylabel("Frecuencia", fontsize=14)
ax.set_facecolor("#222222")
fig.patch.set_facecolor("#222222")
ax.tick_params(axis='x', labelsize=12)
ax.tick_params(axis='y', labelsize=12)
ax.grid(axis='y', linestyle='--', alpha=0.3)

st.pyplot(fig)

# =====================================================================================
# 🔹 3️⃣ Gráfico de Dispersión - Top 100 Calificación vs. Opiniones
st.header("🔍 Calificación vs. Número de Opiniones")
st.markdown("Representación de los 100 mejores restaurantes según calificación y número de opiniones. El color indica el puntaje normalizado.")

fig, ax = plt.subplots(figsize=(14, 10))
scatter = ax.scatter(
    top_100_restaurantes["Calificación"],
    top_100_restaurantes["Número de Opiniones"],
    c=top_100_restaurantes["Puntaje Normalizado"],
    cmap="Blues",
    s=100,
    alpha=0.9,
    edgecolors="white"
)

cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label("Puntaje Normalizado", fontsize=12)

ax.set_title("Top 100 Restaurantes: Calificación vs Número de Opiniones", fontsize=20, fontweight="bold")
ax.set_xlabel("Calificación", fontsize=14)
ax.set_ylabel("Número de Opiniones", fontsize=14)
ax.set_facecolor("#111111")
fig.patch.set_facecolor("#111111")
ax.grid(alpha=0.3)

st.pyplot(fig)

# =====================================================================================
# 🔹 4️⃣ Mapa de Calor - Restaurantes en Tijuana (Estilo Dark)
st.header("📍 Mapa de Calor de Restaurantes en Tijuana")
st.markdown("Este mapa interactivo muestra la concentración de restaurantes en Tijuana, resaltando las zonas con mayor actividad.")

# Configurar mapa
m = folium.Map(location=[32.5149, -117.0382], zoom_start=12, tiles="CartoDB dark_matter")

# Configuración del gradiente
gradient_custom = {
    0.0: "#0000FF",  # Azul
    0.4: "#4B0082",  # Índigo
    0.6: "#FF8C00",  # Naranja
    0.8: "#FF0000",  # Rojo
    1.0: "#FFFF00"   # Amarillo
}

# Datos para el HeatMap
heat_data = df[["Latitud", "Longitud"]].values.tolist()
HeatMap(heat_data, gradient=gradient_custom, radius=15, blur=20, max_zoom=1).add_to(m)

st_folium(m, width=1000, height=600)

# =====================================================================================
# 🔹 5️⃣ Mostrar Datos
st.header("📋 Top 15 Restaurantes")
st.markdown("Aquí puedes consultar los detalles de los 15 restaurantes mejor calificados según el puntaje normalizado.")
top_15_reset = top_15_restaurantes.reset_index(drop=True)
top_15_reset.index += 1
st.dataframe(top_15_reset[["Nombre", "Número de Opiniones", "Calificación", "Puntaje Normalizado"]])
