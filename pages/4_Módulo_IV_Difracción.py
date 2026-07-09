import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from utils_math import calcular_difraccion_rendija, calcular_difraccion_rectangular
# Configuración de la página web
st.set_page_config(page_title="Módulo IV: Difracción", layout="wide")

st.title("Módulo IV: Difracción de Fraunhofer")
st.markdown("Estudio del ensanchamiento de la luz al atravesar aperturas finas (Límite de Campo Lejano).")

# --- BARRA LATERAL (CONTROLES) ---
st.sidebar.header("Geometría de la Apertura")
geometria = st.sidebar.radio("Tipo de Apertura", ["Rendija Simple (1D)", "Apertura Rectangular (2D)"])

st.sidebar.divider()

st.sidebar.header("Parámetros del Sistema")
lam_nm = st.sidebar.slider("Longitud de Onda λ (nm)", 380, 750, 532, 1)
a_mm = st.sidebar.slider("Ancho de la apertura 'a' (mm)", 0.01, 0.50, 0.08, 0.01)

# El alto de la rendija solo importa si es rectangular
if geometria == "Apertura Rectangular (2D)":
    b_mm = st.sidebar.slider("Alto de la apertura 'b' (mm)", 0.01, 0.50, 0.15, 0.01)
else:
    # Corrección: 0.0 anula el encogimiento en Y, haciendo que las franjas llenen la pantalla
    b_mm = 0.0 

L_cm = st.sidebar.slider("Distancia a la Pantalla L (cm)", 10, 500, 100, 10)
tamano_cm = st.sidebar.slider("Ventana de Observación (cm)", 1.0, 10.0, 3.0, 0.5)

st.sidebar.divider()

st.sidebar.header("Visualización")
escala = st.sidebar.radio("Escala de Intensidad", ["Lineal", "Logarítmica"], 
                          help="La escala logarítmica permite visualizar los máximos secundarios de baja intensidad.")

# --- 1. SECCIÓN SUPERIOR: FUNDAMENTO TEÓRICO ---
st.subheader("Fundamento Teórico")
st.markdown("En la aproximación de Fraunhofer (campo lejano), la irradiancia proyectada por una apertura rectangular está modelada por funciones *sinc*:")

col_eq1, col_eq2 = st.columns(2)
with col_eq1:
    st.latex(r"\vphantom{\Bigg|} I(x,y) = I_0 \text{sinc}^2(\alpha) \text{sinc}^2(\beta)")
with col_eq2:
    st.latex(r"\vphantom{\Bigg|} \alpha = \frac{\pi a x}{\lambda L}, \quad \beta = \frac{\pi b y}{\lambda L}")
st.divider()

# --- 2. SECCIÓN CENTRAL: GRÁFICAS LADO A LADO ---
st.subheader("Visualización del Patrón de Difracción")

# --- LÓGICA DE SELECCIÓN DE GEOMETRÍA ---
if geometria == "Rendija Simple (1D)":
    # Llama a la función rigurosa de 1D (no requiere b_mm)
    X, Y, intensidad = calcular_difraccion_rendija(lam_nm, a_mm, L_cm, tamano_cm)
else:
    # Llama a la función rigurosa de 2D (requiere a_mm y b_mm)
    X, Y, intensidad = calcular_difraccion_rectangular(lam_nm, a_mm, b_mm, L_cm, tamano_cm)

# Definir colores
if lam_nm < 495: colormap, linecolor = 'Blues', 'blue'
elif lam_nm < 570: colormap, linecolor = 'Greens', 'green'
elif lam_nm < 620: colormap, linecolor = 'Oranges', 'orange'
else: colormap, linecolor = 'Reds', 'red'

# --- LÓGICA DE ESCALAS ---
# Creamos dos contenedores para las gráficas
col_2d, col_1d = st.columns(2, gap="large")

if escala == "Logarítmica":
    norm = mcolors.LogNorm(vmin=1e-3, vmax=1.0)
    plot_data = np.clip(intensidad, 1e-4, 1.0)
else:
    # Corrección de contraste: vmax=0.4 satura el pico central 
    # para que las franjas secundarias brillen más en escala lineal
    norm = mcolors.Normalize(vmin=0.0, vmax=0.4) 
    plot_data = intensidad

with col_2d:
    st.markdown(f"**Proyección 2D (Escala {escala})**")
    fig_2d, ax_2d = plt.subplots(figsize=(6, 4.5))
    cax = ax_2d.imshow(intensidad, extent=[-tamano_cm/2, tamano_cm/2, -tamano_cm/2, tamano_cm/2], 
                       cmap=colormap, origin='lower', aspect='auto', norm=norm)
    ax_2d.set_xlabel("X (cm)"); ax_2d.set_ylabel("Y (cm)")
    fig_2d.colorbar(cax, ax=ax_2d, label="Intensidad")
    st.pyplot(fig_2d)

with col_1d:
    st.markdown(f"**Perfil en X (Escala {escala})**")
    fig_1d, ax_1d = plt.subplots(figsize=(6, 4.5))
    eje_x_cm = X[0, :] * 100.0
    perfil_1d = plot_data[plot_data.shape[0] // 2, :]
    
    ax_1d.plot(eje_x_cm, perfil_1d, color=linecolor, linewidth=2)
    ax_1d.fill_between(eje_x_cm, perfil_1d, 1e-4 if escala=="Logarítmica" else 0, color=linecolor, alpha=0.2)
    
    if escala == "Logarítmica":
        ax_1d.set_yscale('log')
        ax_1d.set_ylim(1e-4, 1.1)
    else:
        ax_1d.set_ylim(0, 1.05)
        
    ax_1d.set_xlim(-tamano_cm/2, tamano_cm/2)
    ax_1d.set_xlabel("Posición X (cm)")
    ax_1d.set_ylabel("Intensidad")
    ax_1d.grid(True, alpha=0.4)
    st.pyplot(fig_1d)

st.divider()

# --- 3. SECCIÓN INFERIOR: ANÁLISIS CUANTITATIVO ---
st.subheader("Análisis Cuantitativo")
st.markdown("El ancho del máximo central (distancia entre los primeros mínimos a ambos lados) es el principal indicador del ensanchamiento por difracción:")
st.latex(r"W = \frac{2\lambda L}{a}")

lam_m, L_m, a_m = lam_nm * 1e-9, L_cm * 1e-2, a_mm * 1e-3
ancho_central_cm = ((2 * lam_m * L_m) / a_m) * 100.0
x1_cm = ancho_central_cm / 2.0

# Calculamos analíticamente dónde debería estar el pico para saber si cabe en la pantalla
posicion_esperada_pico_cm = 1.4303 * x1_cm

col_metric1, col_metric2, col_metric3 = st.columns(3)
with col_metric1:
    st.metric(label="Ancho del Máximo Central (W)", value=f"{ancho_central_cm:.3f} cm")
with col_metric2:
    st.metric(label="Posición de los Primeros Mínimos", value=f"± {x1_cm:.3f} cm")

# Validación: ¿El pico secundario está dentro del arreglo numérico actual?
if posicion_esperada_pico_cm > (tamano_cm / 2.0):
    with col_metric3:
        st.metric(label="Irradiancia 1er Máx. Secundario", value="Ampliar ventana")
else:
    # Extraemos el perfil transversal exacto de la matriz de intensidad
    eje_x_cm = X[0, :] * 100.0
    perfil_real_1d = intensidad[intensidad.shape[0] // 2, :]
    
    # Buscamos el valor máximo en la región que está más allá del primer mínimo
    mascara_region_secundaria = eje_x_cm > (x1_cm * 1.01)
    if np.any(mascara_region_secundaria):
        irradiancia_secundaria = np.max(perfil_real_1d[mascara_region_secundaria])
    else:
        irradiancia_secundaria = 0.0
        
    with col_metric3:
        st.metric(label="Irradiancia 1er Máx. Secundario", value=f"{irradiancia_secundaria:.4f} I₀")