import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap

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

fig1, ax1 = plt.subplots(figsize=(2.5, 3))  

# 🔹 Estilo del gráfico con marcos
colors = sns.color_palette("Blues", n_colors=10)
sns.barplot(
    data=top_10_restaurantes.sort_values(by="Puntaje Normalizado"),
    y="Nombre",
    x="Puntaje Normalizado",
    palette=colors,
    ax=ax1,
    alpha=0.9,
    edgecolor="white"
)

for i, valor in enumerate(top_10_restaurantes.sort_values(by="Puntaje Normalizado")["Puntaje Normalizado"]):
    ax1.text(valor + 0.05, i, f"{valor:.2f}", ha='left', va='center', fontsize=5, color='white')

for spine in ax1.spines.values():
    spine.set_edgecolor('white')
    spine.set_linewidth(1.2)

ax1.set_title("Top 10 Restaurantes Mejor Calificados", fontsize=8, fontweight="bold", color="white")
ax1.set_xlabel("Puntaje Normalizado (0 a 5)", fontsize=6, color="white")
ax1.set_ylabel("")
ax1.set_facecolor("#222222")
fig1.patch.set_facecolor("#222222")
ax1.tick_params(axis='x', labelsize=6, colors='white')
ax1.tick_params(axis='y', labelsize=6, colors='white')
ax1.grid(axis='x', linestyle='--', alpha=0.3, color='gray')

st.pyplot(fig1)

# ----------------------------------------------------------------------------------------
# 🔹 Gráfico 2: Gráfico de Dispersión - Calificación vs Opiniones
st.header("📌 Calificación vs Número de Opiniones")

fig2, ax2 = plt.subplots(figsize=(5, 3))
scatter = ax2.scatter(
    top_100_restaurantes["Calificación"],
    top_100_restaurantes["Número de Opiniones"],
    c=top_100_restaurantes["Puntaje Normalizado"],
    cmap="Blues",
    s=50,
    edgecolor="white",
    alpha=0.9
)

for spine in ax2.spines.values():
    spine.set_edgecolor('white')
    spine.set_linewidth(1.2)

cbar = plt.colorbar(scatter)
cbar.set_label("Puntaje Normalizado", color="white")
cbar.ax.yaxis.set_tick_params(color="white")
plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="white")

ax2.set_title("Calificación vs Número de Opiniones", fontsize=10, fontweight="bold", color="white")
ax2.set_xlabel("Calificación", fontsize=8, color="white")
ax2.set_ylabel("Número de Opiniones", fontsize=8, color="white")
ax2.set_facecolor("#222222")
fig2.patch.set_facecolor("#222222")
ax2.tick_params(axis="x", labelsize=6, colors="white")
ax2.tick_params(axis="y", labelsize=6, colors="white")
ax2.grid(True, linestyle="--", alpha=0.3, color="gray")

st.pyplot(fig2)

# ----------------------------------------------------------------------------------------
# 🔹 Gráfico 3: Distribución de Categorías
st.header("📊 Distribución de Categorías")

st.markdown("""
Este gráfico de pastel muestra la **distribución de los restaurantes** según su categoría en UberEats Tijuana.
""")

# ✅ Contar la cantidad de restaurantes por categoría
categoria_counts = df["Categoría"].value_counts()

# ✅ Configurar la paleta de colores y ajustar etiquetas
colors = sns.color_palette("coolwarm", len(categoria_counts))

fig5, ax5 = plt.subplots(figsize=(4, 4))
wedges, texts, autotexts = ax5.pie(
    categoria_counts,
    labels=categoria_counts.index,
    autopct='%1.0f%%',
    colors=colors,
    startangle=140,
    wedgeprops={"edgecolor": "white"},
    textprops={'fontsize': 10, 'color': 'white'}  # 🔹 Color de textos en blanco
)

# ✅ Cambiar el color de las etiquetas manualmente
for text in texts:
    text.set_color("white")  # 🔹 Establecer color de las categorías en blanco

# ✅ Ajustar el título
ax5.set_title("Distribución de Categorías", fontsize=12, fontweight="bold", color="white")

# ✅ Fondo oscuro
fig5.patch.set_facecolor("#222222")

# ✅ Mostrar en Streamlit
st.pyplot(fig5)


# ----------------------------------------------------------------------------------------
# 🔹 Mapa de Calor
st.header("📍 Mapa de Calor de Restaurantes en Tijuana")

m = folium.Map(location=[32.5149, -117.0382], zoom_start=12, tiles="CartoDB dark_matter")
heat_data = df[["Latitud", "Longitud"]].values.tolist()
HeatMap(heat_data, radius=15, blur=20).add_to(m)
st_folium(m, width=1000, height=600)

# ----------------------------------------------------------------------------------------
# ✅ Mostrar el dataset
st.header("📋 Top 10 Restaurantes")
top_10_restaurantes.index += 1
st.dataframe(top_10_restaurantes[["Nombre", "Número de Opiniones", "Calificación", "Puntaje Normalizado"]])

# ✅ Mensaje final
st.success("✅ Dashboard cargado exitosamente.")
