import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from utils_math import calcular_patron_young

# Configuración de la página web
st.set_page_config(page_title="Módulo III: Interferencia", layout="wide")

st.title("Módulo III: Interferencia y Ondas")
st.markdown("Simulación rigurosa del patrón de interferencia por división de frente de onda y amplitud.")

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

    # --- 1. SECCIÓN SUPERIOR: FUNDAMENTO TEÓRICO ---
    st.subheader("Fundamento Teórico")
    st.markdown("La intensidad es resultado del desfase entre dos ondas esféricas emergentes:")
    
    col_eq1, col_eq2 = st.columns(2)
    with col_eq1:
        st.latex(r"\vphantom{\Bigg|} I(y) = 4I_0 \cos^2 \left( \frac{\Delta\phi}{2} \right)")
    with col_eq2:
        st.latex(r"\vphantom{\Bigg|} \Delta\phi = \frac{2\pi}{\lambda}(r_2 - r_1)")
        
    st.info("**Nota:** Se calculan distancias vectoriales exactas en el espacio, no solo aproximaciones paraxiales.")
    st.divider()

    # --- 2. SECCIÓN CENTRAL: GRÁFICAS LADO A LADO ---
    st.subheader("Visualización del Patrón de Interferencia")
    
    X, Y, intensidad = calcular_patron_young(lam_nm, d_mm, L_cm, tamano_cm)
    
    if lam_nm < 495: colormap, linecolor = 'Blues', 'blue'
    elif lam_nm < 570: colormap, linecolor = 'Greens', 'green'
    elif lam_nm < 620: colormap, linecolor = 'Oranges', 'orange'
    else: colormap, linecolor = 'Reds', 'red'

    col_2d, col_1d = st.columns(2, gap="large")

    with col_2d:
        st.markdown("**Interferograma 2D**")
        fig_2d, ax_2d = plt.subplots(figsize=(6, 4.5))
        cax = ax_2d.imshow(intensidad, extent=[-tamano_cm/2, tamano_cm/2, -tamano_cm/2, tamano_cm/2], cmap=colormap, origin='lower', aspect='auto')
        ax_2d.set_title(f"Patrón de Doble Rendija ($\lambda$ = {lam_nm} nm)")
        ax_2d.set_xlabel("X (cm)")
        ax_2d.set_ylabel("Y (cm)")
        fig_2d.colorbar(cax, ax=ax_2d)
        st.pyplot(fig_2d)

    with col_1d:
        st.markdown("**Perfil Transversal 1D**")
        fig_1d, ax_1d = plt.subplots(figsize=(6, 4.5))
        eje_y_cm = Y[:, 0] * 100.0
        ax_1d.plot(eje_y_cm, intensidad[:, intensidad.shape[1] // 2], color=linecolor, linewidth=2)
        ax_1d.fill_between(eje_y_cm, intensidad[:, intensidad.shape[1] // 2], color=linecolor, alpha=0.2)
        ax_1d.set_xlim(-tamano_cm/2, tamano_cm/2)
        ax_1d.set_ylim(0, 1.05)
        ax_1d.set_xlabel("Posición Y (cm)")
        ax_1d.set_ylabel("Intensidad Relativa")
        ax_1d.grid(True, alpha=0.4)
        st.pyplot(fig_1d)

    st.divider()

   # --- 3. SECCIÓN INFERIOR: ANÁLISIS CUANTITATIVO ---
    st.subheader("Análisis Cuantitativo: Paraxial vs Exacto")
    st.markdown("Comparativa entre el modelo aproximado de los libros de texto y la solución geométrica exacta implementada en este simulador:")
    
    col_eq1, col_eq2 = st.columns(2)
    with col_eq1:
        st.markdown("**Aproximación Paraxial (Ángulos pequeños):**")
        st.latex(r"\Delta y \approx \frac{\lambda L}{d}")
    with col_eq2:
        st.markdown("**Solución Exacta (Intersección Hiperbólica):**")
        st.latex(r"y_1 = \sqrt{\frac{\lambda^2 L^2}{d^2 - \lambda^2} + \frac{\lambda^2}{4}}")
    
    # Conversión de unidades a metros para el cálculo
    lam_m, L_m, d_m = lam_nm * 1e-9, L_cm * 1e-2, d_mm * 1e-3
    
    # Cálculo Paraxial
    delta_y_paraxial_cm = ((lam_m * L_m) / d_m) * 100.0
    
    # Cálculo Exacto
    y1_exacto_cm = np.sqrt((lam_m**2 * L_m**2) / (d_m**2 - lam_m**2) + (lam_m**2 / 4.0)) * 100.0
    
    # Cálculo del error (qué tanto se equivoca la aproximación)
    error_porcentual = abs(y1_exacto_cm - delta_y_paraxial_cm) / y1_exacto_cm * 100.0
    
    # Mostrar métricas
    col_metric1, col_metric2, col_metric3 = st.columns(3)
    with col_metric1:
        st.metric(label="Predicción Paraxial (Δy)", value=f"{delta_y_paraxial_cm:.4f} cm")
    with col_metric2:
        st.metric(label="Posición Exacta (Simulador)", value=f"{y1_exacto_cm:.4f} cm")
    #with col_metric3:
     #   st.metric(label="Error de Aproximación", value=f"{error_porcentual:.4f} %")
else:
    # --- CONTROLES DE MICHELSON ---
    from utils_math import calcular_patron_michelson
    
    st.sidebar.header("Parámetros del Sistema (Michelson)")
    lam_nm = st.sidebar.slider("Longitud de Onda λ (nm)", 380, 750, 632, 1, help="Rojo He-Ne por defecto.")
    delta_d_um = st.sidebar.slider(
    "Desplazamiento del Espejo M2 (μm)", 
    0.000, 50.000, 10.000, 0.001, 
    format="%.3f"  
)
    f_cm = st.sidebar.slider("Focal de Lente Proyectora f (cm)", 5.0, 50.0, 20.0, 1.0)
    tamano_cm = st.sidebar.slider("Ventana de Observación (cm)", 1.0, 20.0, 10.0, 0.5)

    # --- 1. SECCIÓN SUPERIOR: FUNDAMENTO TEÓRICO ---
    st.subheader("Fundamento Teórico")
    st.markdown("Al mover el espejo $M_2$ una distancia $\Delta d$, se induce un desfase que genera anillos de igual inclinación (Haidinger):")
    st.latex(r"\Delta \phi = \frac{4\pi}{\lambda} \Delta d \cos(\theta)")
    st.divider()

    # --- 2. SECCIÓN CENTRAL: GRÁFICAS LADO A LADO ---
    st.subheader("Visualización del Patrón de Interferencia")
    
    X, Y, intensidad = calcular_patron_michelson(lam_nm, delta_d_um, f_cm, tamano_cm)
    
    if lam_nm < 495: colormap, linecolor = 'Blues', 'blue'
    elif lam_nm < 570: colormap, linecolor = 'Greens', 'green'
    elif lam_nm < 620: colormap, linecolor = 'Oranges', 'orange'
    else: colormap, linecolor = 'Reds', 'red'

    col_2d, col_1d = st.columns(2, gap="large")
    
    with col_2d:
        st.markdown("**Anillos de Haidinger (2D)**")
        fig_2d, ax_2d = plt.subplots(figsize=(6, 4.5))
        cax = ax_2d.imshow(intensidad, extent=[-tamano_cm/2, tamano_cm/2, -tamano_cm/2, tamano_cm/2], cmap=colormap, origin='lower', aspect='auto')
        ax_2d.set_title(f"Interferómetro de Michelson ($\lambda$ = {lam_nm} nm)")
        ax_2d.set_xlabel("X (cm)")
        ax_2d.set_ylabel("Y (cm)")
        fig_2d.colorbar(cax, ax=ax_2d)
        st.pyplot(fig_2d)

    with col_1d:
        st.markdown("**Perfil Radial 1D**")
        fig_1d, ax_1d = plt.subplots(figsize=(6, 4.5))
        eje_x_cm = X[0, :] * 100.0
        intensidad_1d = intensidad[intensidad.shape[0] // 2, :]
        
        ax_1d.plot(eje_x_cm, intensidad_1d, color=linecolor, linewidth=2)
        ax_1d.fill_between(eje_x_cm, intensidad_1d, color=linecolor, alpha=0.2)
        ax_1d.set_xlim(-tamano_cm/2, tamano_cm/2)
        ax_1d.set_ylim(0, 1.05)
        ax_1d.set_xlabel("Posición Radial X (cm)")
        ax_1d.set_ylabel("Intensidad Relativa")
        ax_1d.grid(True, alpha=0.4)
        st.pyplot(fig_1d)

    st.divider()

    # --- 3. SECCIÓN INFERIOR: ANÁLISIS DINÁMICO ---
    st.subheader("Análisis Dinámico")
    st.markdown("Cada vez que el espejo se desplaza exactamente **$\lambda/2$**, el patrón central cambia de brillante a oscuro o viceversa.")
    
    paso_lambda = (lam_nm * 1e-3) / 2.0  # en micras
    
    # Extraer el valor exacto del centro de la matriz de intensidad
    centro_idx_y = intensidad.shape[0] // 2
    centro_idx_x = intensidad.shape[1] // 2
    intensidad_central = intensidad[centro_idx_y, centro_idx_x]
    
    col_metric1, col_metric2 = st.columns(2)
    with col_metric1:
        st.metric(label="Sensibilidad (λ/2)", value=f"{paso_lambda:.4f} μm")
    with col_metric2:
        st.metric(label="Intensidad Relativa Central", value=f"{intensidad_central:.3f}")