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

st.set_page_config(page_title="Dashboard Restaurantes Tijuana", layout="wide")
st.title("📊 Dashboard de Restaurantes en UberEats - Tijuana")

# ----------------------------------------------------------------------------------------
# 🔹 Gráfico 1: Top 10 Restaurantes Mejor Calificados (Restaurantes en Eje Vertical)
st.header("🏆 Top 10 Restaurantes Mejor Calificados")

st.markdown("""
Este gráfico muestra los **10 restaurantes mejor calificados** en Tijuana según un puntaje ponderado que toma en cuenta tanto la calificación como el número de opiniones.
""")

fig1, ax1 = plt.subplots(figsize=(4, 3))  # 📏 Tamaño Ajustado

colors = sns.color_palette("Blues", n_colors=10)
sns.barplot(
    data=top_10_restaurantes.sort_values(by="Puntaje Normalizado"),
    y="Nombre",  # 📌 Ahora los nombres están en el lado izquierdo
    x="Puntaje Normalizado",
    palette=colors,
    ax=ax1,
    alpha=0.9,
    edgecolor="white"
)

# 📌 Agregar valores dentro de las barras
for i, valor in enumerate(top_10_restaurantes.sort_values(by="Puntaje Normalizado")["Punt
