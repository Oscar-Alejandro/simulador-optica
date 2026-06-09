import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from utils_math import calcular_patron_young

# Configuración de la página web
st.set_page_config(page_title="Módulo III: Interferencia", layout="wide")

st.title("Módulo III: Interferencia y Ondas")
st.markdown("Simulación rigurosa del patrón de interferencia por división de frente de onda.")

# --- SELECTOR DE EXPERIMENTO ---
st.sidebar.header("Selección de Experimento")
tipo_experimento = st.sidebar.radio(
    "Mecanismo de Interferencia",
    ["Doble Rendija de Young (Div. Frente)", "Interferómetro de Michelson (Div. Amplitud)"]
)

st.sidebar.divider()

if tipo_experimento == "Doble Rendija de Young (Div. Frente)":
    # --- CONTROLES DE YOUNG ---
    st.sidebar.header("Parámetros del Sistema (Young)")
    lam_nm = st.sidebar.slider("Longitud de Onda λ (nm)", 380, 750, 532, 1)
    d_mm = st.sidebar.slider("Separación de Rendijas d (mm)", 0.01, 0.50, 0.10, 0.01)
    L_cm = st.sidebar.slider("Distancia a la Pantalla L (cm)", 10, 500, 100, 10)
    tamano_cm = st.sidebar.slider("Ventana de Observación (cm)", 1.0, 20.0, 5.0, 0.5)

    # --- MOTOR DE GRÁFICOS (YOUNG) ---
    col1, col2 = st.columns([1, 2.5])
    
    with col1:
        st.subheader("Fundamento Teórico")
        st.markdown("La intensidad es resultado del desfase entre dos ondas esféricas emergentes:")
        st.latex(r"I(y) = 4I_0 \cos^2\left(\frac{\Delta \phi}{2}\right)")
        st.latex(r"\Delta \phi = \frac{2\pi}{\lambda}(r_2 - r_1)")
        
        st.info("**Nota:** Se calculan distancias vectoriales exactas en el espacio.")
        st.divider()
        st.subheader("Análisis Cuantitativo")
        st.markdown("En la región central, la separación teórica entre franjas es:")
        st.latex(r"\Delta y \approx \frac{\lambda L}{d}")
        
        lam_m, L_m, d_m = lam_nm * 1e-9, L_cm * 1e-2, d_mm * 1e-3
        delta_y_cm = ((lam_m * L_m) / d_m) * 100.0
        st.metric(label="Separación Teórica (Δy)", value=f"{delta_y_cm:.4f} cm")
        
    with col2:
        X, Y, intensidad = calcular_patron_young(lam_nm, d_mm, L_cm, tamano_cm)
        
        if lam_nm < 495: colormap, linecolor = 'Blues', 'blue'
        elif lam_nm < 570: colormap, linecolor = 'Greens', 'green'
        elif lam_nm < 620: colormap, linecolor = 'Oranges', 'orange'
        else: colormap, linecolor = 'Reds', 'red'

        tab1, tab2 = st.tabs(["Interferograma 2D", "Perfil Transversal 1D"])
        with tab1:
            fig_2d, ax_2d = plt.subplots(figsize=(8, 5))
            cax = ax_2d.imshow(intensidad, extent=[-tamano_cm/2, tamano_cm/2, -tamano_cm/2, tamano_cm/2], cmap=colormap, origin='lower', aspect='auto')
            ax_2d.set_title(f"Patrón de Doble Rendija ($\lambda$ = {lam_nm} nm)")
            fig_2d.colorbar(cax, ax=ax_2d)
            st.pyplot(fig_2d)

        with tab2:
            fig_1d, ax_1d = plt.subplots(figsize=(8, 4))
            eje_y_cm = Y[:, 0] * 100.0
            ax_1d.plot(eje_y_cm, intensidad[:, intensidad.shape[1] // 2], color=linecolor)
            ax_1d.set_xlim(-tamano_cm/2, tamano_cm/2)
            st.pyplot(fig_1d)

else:
    # --- CONTROLES DE MICHELSON ---
    # Importamos dinámicamente la nueva función solo si estamos en esta pestaña
    from utils_math import calcular_patron_michelson
    
    st.sidebar.header("Parámetros del Sistema (Michelson)")
    lam_nm = st.sidebar.slider("Longitud de Onda λ (nm)", 380, 750, 632, 1, help="Rojo He-Ne por defecto.")
    # El desfase es la posición micrométrica del espejo M2 respecto al equilibrio
    delta_d_um = st.sidebar.slider("Desplazamiento del Espejo M2 (μm)", 0.0, 50.0, 10.0, 0.1)
    f_cm = st.sidebar.slider("Focal de Lente Proyectora f (cm)", 5.0, 50.0, 20.0, 1.0)
    tamano_cm = st.sidebar.slider("Ventana de Observación (cm)", 1.0, 20.0, 10.0, 0.5)

    # --- MOTOR DE GRÁFICOS (MICHELSON) ---
    col1, col2 = st.columns([1, 2.5])
    
    with col1:
        st.subheader("Fundamento Teórico")
        st.markdown("Al mover el espejo $M_2$ una distancia $\Delta d$, se induce un desfase que genera anillos de igual inclinación (Haidinger):")
        st.latex(r"\Delta \phi = \frac{4\pi}{\lambda} \Delta d \cos(\theta)")
        
        st.divider()
        st.subheader("Análisis Dinámico")
        st.markdown("Cada vez que el espejo se desplaza exactamente **$\lambda/2$**, el patrón central cambia de brillante a oscuro o viceversa, permitiendo medir distancias a escala nanométrica.")
        
        paso_lambda = (lam_nm * 1e-3) / 2.0  # en micras
        st.metric(label="Sensibilidad (λ/2)", value=f"{paso_lambda:.4f} μm")

    with col2:
        X, Y, intensidad = calcular_patron_michelson(lam_nm, delta_d_um, f_cm, tamano_cm)
        
        if lam_nm < 495: colormap, linecolor = 'Blues', 'blue'
        elif lam_nm < 570: colormap, linecolor = 'Greens', 'green'
        elif lam_nm < 620: colormap, linecolor = 'Oranges', 'orange'
        else: colormap, linecolor = 'Reds', 'red'

        tab1, tab2 = st.tabs(["Anillos de Haidinger (2D)", "Perfil Radial 1D"])
        
        with tab1:
            fig_2d, ax_2d = plt.subplots(figsize=(8, 5))
            cax = ax_2d.imshow(intensidad, extent=[-tamano_cm/2, tamano_cm/2, -tamano_cm/2, tamano_cm/2], cmap=colormap, origin='lower', aspect='auto')
            ax_2d.set_title(f"Interferómetro de Michelson ($\lambda$ = {lam_nm} nm)")
            ax_2d.set_xlabel("X (cm)")
            ax_2d.set_ylabel("Y (cm)")
            fig_2d.colorbar(cax, ax=ax_2d)
            st.pyplot(fig_2d)

        with tab2:
            fig_1d, ax_1d = plt.subplots(figsize=(8, 4))
            # Perfil transversal exacto pasando por el centro
            eje_x_cm = X[0, :] * 100.0
            intensidad_1d = intensidad[intensidad.shape[0] // 2, :]
            
            ax_1d.plot(eje_x_cm, intensidad_1d, color=linecolor, linewidth=2)
            ax_1d.fill_between(eje_x_cm, intensidad_1d, color=linecolor, alpha=0.2)
            ax_1d.set_xlim(-tamano_cm/2, tamano_cm/2)
            ax_1d.set_ylim(0, 1.05)
            ax_1d.grid(True, alpha=0.4)
            st.pyplot(fig_1d)