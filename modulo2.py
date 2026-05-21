import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from utils_math import calcular_snell

# Configuración de la página
st.set_page_config(page_title="Módulo II: Reflexión y Refracción", layout="centered")

st.title("Módulo II: Leyes de Reflexión y Refracción")
st.markdown("Simulador interactivo para el análisis de fronteras dieléctricas.")

# Panel lateral para los controles (Inputs)
st.sidebar.header("Parámetros del Sistema")
n1 = st.sidebar.slider("Índice n1 (Medio de Incidencia)", min_value=1.0, max_value=3.0, value=1.0, step=0.01)
n2 = st.sidebar.slider("Índice n2 (Medio de Transmisión)", min_value=1.0, max_value=3.0, value=1.5, step=0.01)
theta_i = st.sidebar.slider("Ángulo de Incidencia θi (grados)", min_value=0.0, max_value=90.0, value=45.0, step=1.0)

# Llamada a nuestro motor matemático
theta_t, tir, theta_c = calcular_snell(n1, n2, theta_i)

# --- NUEVA SECCIÓN: LÓGICA GRÁFICA ---
def graficar_sistema(n1, n2, theta_i, theta_t, tir):
    """Genera la visualización 2D de los rayos usando Matplotlib"""
    fig, ax = plt.subplots(figsize=(7, 7))
    
    # Dibujar los medios (colores de fondo)
    ax.axhspan(0, 1, facecolor='#e6f2ff', alpha=0.8) # Medio 1
    ax.axhspan(-1, 0, facecolor='#e6ffe6', alpha=0.8) # Medio 2
    
    # Frontera y línea normal
    ax.axhline(0, color='black', linewidth=2)
    ax.axvline(0, color='gray', linestyle='--')
    
    # Conversión de ángulos a radianes para trigonometría
    rad_i = np.radians(theta_i)
    
    # 1. Rayo Incidente (Viene del cuadrante II hacia el origen)
    x_inc, y_inc = -np.sin(rad_i), np.cos(rad_i)
    ax.plot([x_inc, 0], [y_inc, 0], color='red', linewidth=3, label='Rayo Incidente')
    
    # 2. Rayo Reflejado (Va del origen al cuadrante I)
    x_ref, y_ref = np.sin(rad_i), np.cos(rad_i)
    ax.plot([0, x_ref], [0, y_ref], color='blue', linewidth=3, label='Rayo Reflejado')
    
    # 3. Rayo Refractado (Solo si no hay TIR)
    if not tir:
        rad_t = np.radians(theta_t)
        x_tra, y_tra = np.sin(rad_t), -np.cos(rad_t)
        ax.plot([0, x_tra], [0, y_tra], color='green', linewidth=3, label='Rayo Refractado')
    else:
        ax.text(0, -0.5, "Reflexión Total Interna", horizontalalignment='center', 
                fontsize=14, color='red', weight='bold')

    # Configuraciones estéticas del gráfico
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_aspect('equal') # Para que los ángulos no se deformen
    ax.axis('off') # Quitamos los ejes numéricos para que se vea más limpio
    ax.legend(loc='upper right', framealpha=0.9)
    
    # Textos de los índices de refracción
    ax.text(-1.1, 0.8, f"n1 = {n1:.2f}", fontsize=12, weight='bold', bbox=dict(facecolor='white', alpha=0.7))
    ax.text(-1.1, -0.8, f"n2 = {n2:.2f}", fontsize=12, weight='bold', bbox=dict(facecolor='white', alpha=0.7))
    
    return fig

# --- DESPLIEGUE DEL FRONTEND ---
col1, col2 = st.columns([1, 1.5]) # Dividimos la pantalla en dos columnas

with col1:
    st.subheader("Resultados Analíticos")
    st.write(f"**Ángulo de Incidencia:** {theta_i}°")
    
    if tir:
        st.error("¡Reflexión Total Interna!")
        st.write(f"Ángulo crítico: **{theta_c:.2f}°**")
    else:
        st.success("Refracción transmitida")
        st.write(f"**Ángulo de Refracción:** {theta_t:.2f}°")
        if theta_c:
            st.info(f"Ángulo crítico de frontera: {theta_c:.2f}°")

with col2:
    # Renderizamos el gráfico generado
    figura = graficar_sistema(n1, n2, theta_i, theta_t, tir)
    st.pyplot(figura)