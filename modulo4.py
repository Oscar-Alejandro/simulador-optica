import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from utils_math import calcular_difraccion_rendija, calcular_difraccion_rectangular

# Configuración de la página web
st.set_page_config(page_title="Módulo IV: Difracción", layout="wide")

st.title("Módulo IV: Difracción de la Luz")
st.markdown("Simulación del patrón de difracción de Fraunhofer en condiciones de campo lejano.")

# --- BARRA LATERAL (CONTROLES) ---
st.sidebar.header("Configuración de la Apertura")
geometria = st.sidebar.radio("Geometría del Obstáculo", ["Rendija Simple (1D)", "Apertura Rectangular (2D)"])

st.sidebar.divider()
st.sidebar.header("Parámetros Físicos")

lam_nm = st.sidebar.slider("Longitud de Onda λ (nm)", 380, 750, 532, 1)
ancho_a_mm = st.sidebar.slider("Ancho de la apertura 'a' (mm)", 0.02, 0.50, 0.08, 0.01)

if geometria == "Apertura Rectangular (2D)":
    altura_b_mm = st.sidebar.slider("Altura de la apertura 'b' (mm)", 0.02, 0.50, 0.12, 0.01)

L_cm = st.sidebar.slider("Distancia a la Pantalla L (cm)", 20, 300, 100, 10)
tamano_cm = st.sidebar.slider("Ventana de Observación (cm)", 1.0, 15.0, 6.0, 0.5)

# --- MOTOR DE GRÁFICOS Y ANÁLISIS ---
col1, col2 = st.columns([1, 2.5])

with col1:
    st.subheader("Fundamento Teórico")
    if geometria == "Rendija Simple (1D)":
        st.markdown("La difracción de una rendija vertical distribuye la irradiancia horizontalmente siguiendo una función matemática $\text{sinc}^2$:")
        st.latex(r"I(x) = I_0 \left[ \frac{\sin(\alpha)}{\alpha} \right]^2")
        st.latex(r"\alpha = \frac{\pi a \sin\theta_x}{\lambda}")
        
        st.divider()
        st.subheader("Análisis Cuantitativo")
        st.markdown("El ancho total del máximo central (distancia entre los dos primeros mínimos oscuros a la izquierda y derecha) está definido por:")
        st.latex(r"W = \frac{2\lambda L}{a}")
        
        # Cálculo analítico del ancho central
        lam_m, a_m, L_m = lam_nm * 1e-9, ancho_a_mm * 1e-3, L_cm * 1e-2
        W_cm = ((2.0 * lam_m * L_m) / a_m) * 100.0
        st.metric(label="Ancho del Máximo Central (W)", value=f"{W_cm:.4f} cm")
    else:
        st.markdown("Para una apertura rectangular, las difracciones vertical y horizontal se superponen independientemente, modulando la irradiancia en ambos ejes:")
        st.latex(r"I(x,y) = I_0 \;\text{sinc}^2(\alpha)\;\text{sinc}^2(\beta)")
        st.latex(r"\beta = \frac{\pi b \sin\theta_y}{\lambda}")
        st.info("**Sugerencia:** Modifica el ancho y la altura de forma asimétrica en el panel de control para observar cómo el patrón óptico se invierte geométricamente en la pantalla debido a la transformada de Fourier.")

with col2:
    # Ejecución de los motores analíticos
    if geometria == "Rendija Simple (1D)":
        X, Y, intensidad = calcular_difraccion_rendija(lam_nm, ancho_a_mm, L_cm, tamano_cm)
    else:
        X, Y, intensidad = calcular_difraccion_rectangular(lam_nm, ancho_a_mm, altura_b_mm, L_cm, tamano_cm)

    # Selector cromático según longitud de onda
    if lam_nm < 495: colormap, linecolor = 'Blues_r', 'blue'
    elif lam_nm < 570: colormap, linecolor = 'Greens_r', 'green'
    elif lam_nm < 620: colormap, linecolor = 'Oranges_r', 'orange'
    else: colormap, linecolor = 'Reds_r', 'red'

    tab1, tab2 = st.tabs(["Patrón de Difracción (2D)", "Perfil de Irradiancia (1D)"])
    
    with tab1:
        st.subheader("Visualización en la Pantalla de Proyección")
        fig_2d, ax_2d = plt.subplots(figsize=(8, 5))
        
        cax = ax_2d.imshow(intensidad, extent=[-tamano_cm/2, tamano_cm/2, -tamano_cm/2, tamano_cm/2], 
                           cmap=colormap, origin='lower', aspect='auto', vmax=0.15 if geometria == "Apertura Rectangular (2D)" else 1.0)
        # Nota: Usamos un vmax bajo en la rectangular para poder apreciar los lóbulos secundarios que son muy tenues
        
        ax_2d.set_xlabel("X (cm)")
        ax_2d.set_ylabel("Y (cm)")
        ax_2d.set_title(f"Patrón de Difracción de Fraunhofer (λ = {lam_nm} nm)")
        fig_2d.colorbar(cax, ax=ax_2d, label="Intensidad Relativa")
        st.pyplot(fig_2d)

    with tab2:
        st.subheader("Corte Transversal Horizontal (Y = 0)")
        fig_1d, ax_1d = plt.subplots(figsize=(8, 4))
        
        # Extraemos la fila central para ver los lóbulos oscilantes a lo largo de X
        fila_centro_y = intensidad.shape[0] // 2
        intensidad_1d = intensidad[fila_centro_y, :]
        eje_x_cm = X[0, :] * 100.0  # Conversión rigurosa a centímetros
        
        ax_1d.plot(eje_x_cm, intensidad_1d, color=linecolor, linewidth=2)
        ax_1d.fill_between(eje_x_cm, intensidad_1d, color=linecolor, alpha=0.15)
        
        ax_1d.set_xlabel("Posición en la pantalla X (cm)")
        ax_1d.set_ylabel("Intensidad I/I₀")
        ax_1d.set_xlim(-tamano_cm/2, tamano_cm/2)
        ax_1d.set_ylim(0, 1.05)
        ax_1d.grid(True, alpha=0.3)
        st.pyplot(fig_1d)