import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from utils_math import calcular_snell, analizar_camino_optico

# Configuración de la página web
st.set_page_config(page_title="Módulo II: Reflexión y Refracción", layout="wide")

st.title("Módulo II: Reflexión y Refracción")
st.markdown("Estudio de la Ley de Snell y verificación analítica del Principio de Fermat.")

# --- BARRA LATERAL (CONTROLES) ---
st.sidebar.header("Parámetros del Sistema (Snell)")
n1 = st.sidebar.slider("Índice de refracción (Medio 1)", 1.0, 3.0, 1.0, 0.01)
n2 = st.sidebar.slider("Índice de refracción (Medio 2)", 1.0, 3.0, 1.5, 0.01)
theta_i_deg = st.sidebar.slider("Ángulo de Incidencia θ₁ (°)", 0.0, 89.9, 45.0, 0.1)

st.sidebar.divider()

st.sidebar.header("Principio de Fermat")
st.sidebar.markdown("Encuentra la trayectoria real minimizando el camino óptico entre A y B.")
x_interfaz = st.sidebar.slider("Desliza el punto de incidencia 'x' en la frontera", 
                               min_value=-5.0, max_value=5.0, value=0.0, step=0.1)

# --- CÁLCULOS MATEMÁTICOS BÁSICOS ---
# 1. Ley de Snell
theta_t_deg, tir, theta_critico = calcular_snell(n1, n2, theta_i_deg)

# 2. Fermat (Puntos fijos para el análisis OPL)
x_A, y_A = -4.0, 4.0
x_B, y_B = 4.0, -4.0

opl_puntual, x_array, opl_array, x_min, opl_min = analizar_camino_optico(
    n1, n2, x_A, y_A, x_B, y_B, x_interfaz
)
def calcular_fresnel(n1, n2, theta_i_rad):
    """Devuelve Reflectancia (R) y Transmitancia (T) basadas en Fresnel."""
    sin_t = (n1 / n2) * np.sin(theta_i_rad)
    if sin_t >= 1.0:
        return 1.0, 0.0  # Reflexión Total Interna
    
    theta_t_rad = np.arcsin(sin_t)
    if theta_i_rad == 0.0:
        R = ((n1 - n2) / (n1 + n2))**2
        return R, 1.0 - R
        
    rs = (n1 * np.cos(theta_i_rad) - n2 * np.cos(theta_t_rad)) / (n1 * np.cos(theta_i_rad) + n2 * np.cos(theta_t_rad))
    rp = (n1 * np.cos(theta_t_rad) - n2 * np.cos(theta_i_rad)) / (n1 * np.cos(theta_t_rad) + n2 * np.cos(theta_i_rad))
    
    R = (rs**2 + rp**2) / 2.0
    return R, 1.0 - R
# --- MOTOR DE GRÁFICOS Y CONTENEDORES ---
col1, col2 = st.columns([1, 2.5])

with col1:
    st.subheader("Fundamento Teórico")
    st.markdown("La Ley de Snell describe la refracción geométrica en la frontera:")
    st.latex(r"n_1 \sin(\theta_i) = n_2 \sin(\theta_t)")
    
    # Notificaciones del estado de Snell
    if tir:
        st.error(f"**Reflexión Total Interna (TIR)**\nEl ángulo crítico es {theta_critico:.2f}°.")
    else:
        st.success(f"**Ángulo de Refracción:** {theta_t_deg:.2f}°")
        if theta_critico:
            st.info(f"Ángulo crítico del sistema: {theta_critico:.2f}°")

    st.divider()
    
    st.subheader("Principio de Fermat")
    st.markdown("Establece que la luz sigue la trayectoria que minimiza el tiempo de viaje o **Camino Óptico (OPL)**:")
    st.latex(r"OPL(x) = n_1 L_1 + n_2 L_2")
    
    st.metric(label="Camino Óptico Actual", value=f"{opl_puntual:.4f}")
    st.metric(label="Mínimo Absoluto (Fermat)", value=f"{opl_min:.4f}")
    
    if abs(x_interfaz - x_min) < 0.15:
        st.success(f"¡Trayectoria Real! x ≈ {x_min:.2f} cm cumple la Ley de Snell.")
    else:
        st.warning("Trayectoria virtual (físicamente imposible).")

with col2:
    # --- CREACIÓN DE PESTAÑAS PARALELAS ---
    tab1, tab2 = st.tabs(["1. Trazado de Rayos (Snell)", "2. Minimización de Camino Óptico (Fermat)"])
    
    # ----------------------------------------------------
    # PESTAÑA 1: DEMOSTRACIÓN CLÁSICA DE SNELL
    # ----------------------------------------------------
    with tab1:
        st.subheader("Visualización Geométrica de la Ley de Snell")
        fig_snell, ax_snell = plt.subplots(figsize=(8, 5))
        
        # Frontera y normal
        ax_snell.axhline(0, color='black', linewidth=2)
        ax_snell.axvline(0, color='gray', linestyle=':', alpha=0.6)
        
        # Colores de fondo para identificar los medios
        ax_snell.fill_between([-5, 5], 0, 5, color='blue', alpha=0.03)
        ax_snell.fill_between([-5, 5], -5, 0, color='green', alpha=0.03)
        ax_snell.text(-4.5, 4, f"Medio 1 (n₁ = {n1})", weight='bold')
        ax_snell.text(-4.5, -4, f"Medio 2 (n₂ = {n2})", weight='bold')
        
        # Cálculo de vectores de los rayos (longitud fija de 4.5 unidades)
        rad_i = np.radians(theta_i_deg)
        x_inc = -np.sin(rad_i) * 4.5
        y_inc = np.cos(rad_i) * 4.5
        
        # Dibujar Rayo Incidente hacia el origen (0,0)
        ax_snell.plot([x_inc, 0], [y_inc, 0], color='red', linewidth=3, label="Rayo Incidente")
        
        # Dibujar Rayo Reflejado (siempre existe por reflexión parcial)
        ax_snell.plot([0, -x_inc], [0, y_inc], color='orange', linewidth=2, linestyle='--', label="Rayo Reflejado")
        
        # Dibujar Rayo Refractado si no hay TIR
        if not tir:
            rad_t = np.radians(theta_t_deg)
            x_ref = np.sin(rad_t) * 4.5
            y_ref = -np.cos(rad_t) * 4.5
            ax_snell.plot([0, x_ref], [0, y_ref], color='green', linewidth=3, label="Rayo Refractado")
            
        ax_snell.set_xlim(-5, 5)
        ax_snell.set_ylim(-5, 5)
        ax_snell.set_aspect('equal')
        ax_snell.axis('off')
        ax_snell.legend(loc='upper right')
        
        st.pyplot(fig_snell)

    # ----------------------------------------------------
    # PESTAÑA 2: DEMOSTRACIÓN DE FERMAT
    # ----------------------------------------------------
    with tab2:
        st.subheader("Análisis de Trayectorias Variacionales")
        
        # Sub-columnas dentro de la pestaña para optimizar el espacio horizontal
        sub_col1, sub_col2 = st.columns(2)
        
        with sub_col1:
            st.markdown("**Camino Geométrico de Prueba**")
            fig_geom, ax_geom = plt.subplots(figsize=(6, 5))
            
            ax_geom.axhline(0, color='black', linewidth=1.5)
            # Normal en el punto de incidencia
            ax_geom.axvline(x_interfaz, color='gray', linestyle='-.', alpha=0.6)
            
            # 1. CÁLCULO DE ÁNGULOS DEL RAYO DE PRUEBA
            # Vector Incidente (de A hacia la interfaz)
            vec_inc = np.array([x_interfaz - x_A, 0 - y_A])
            ang_inc_rad = np.arctan(abs(vec_inc[0]) / abs(vec_inc[1])) # Ángulo con la vertical
            
            # Vector Transmitido (de la interfaz hacia B)
            vec_trans = np.array([x_B - x_interfaz, y_B - 0])
            ang_trans_rad = np.arctan(abs(vec_trans[0]) / abs(vec_trans[1]))
            
            # 2. CÁLCULO DE INTENSIDADES (FRESNEL)
            R, T = calcular_fresnel(n1, n2, ang_inc_rad)
            grosor_base = 4.0
            
            # 3. DIBUJO DE RAYOS (Con grosores dinámicos)
            # Rayo Incidente (100% de intensidad)
            ax_geom.plot([x_A, x_interfaz], [y_A, 0], color='red', linewidth=grosor_base, label="Incidente")
            # Rayo Reflejado (Se dibuja hacia arriba, ancho = R%)
            x_refl = x_interfaz + (x_interfaz - x_A)
            ax_geom.plot([x_interfaz, x_refl], [0, y_A], color='orange', linestyle='--', linewidth=grosor_base * R, alpha=0.8)
            # Rayo Refractado hacia B (ancho = T%)
            ax_geom.plot([x_interfaz, x_B], [0, y_B], color='green', linewidth=grosor_base * T, label="Transmitido")
            
            # 4. DIBUJO DE ARCOS DE ÁNGULOS Y ETIQUETAS
            r_arc = 1.0 # Radio del arco
            # Arco incidente
            ang_normal_up = np.pi/2
            ang_vec_inc = np.arctan2(-vec_inc[1], -vec_inc[0]) # Invertido para dibujar desde el origen
            t_arc_i = np.linspace(ang_normal_up, ang_vec_inc, 20)
            ax_geom.plot(x_interfaz + r_arc*np.cos(t_arc_i), r_arc*np.sin(t_arc_i), color='red', lw=1.5)
            ax_geom.text(x_interfaz + 1.3*r_arc*np.cos((ang_normal_up+ang_vec_inc)/2), 
                         1.3*r_arc*np.sin((ang_normal_up+ang_vec_inc)/2), 
                         f"$\\theta_i = {np.degrees(ang_inc_rad):.1f}^\\circ$", color='red', weight='bold')

            # Arco transmitido
            ang_normal_down = -np.pi/2
            ang_vec_trans = np.arctan2(vec_trans[1], vec_trans[0])
            t_arc_t = np.linspace(ang_normal_down, ang_vec_trans, 20)
            ax_geom.plot(x_interfaz + r_arc*np.cos(t_arc_t), r_arc*np.sin(t_arc_t), color='green', lw=1.5)
            ax_geom.text(x_interfaz + 1.3*r_arc*np.cos((ang_normal_down+ang_vec_trans)/2), 
                         1.3*r_arc*np.sin((ang_normal_down+ang_vec_trans)/2), 
                         f"$\\theta_t = {np.degrees(ang_trans_rad):.1f}^\\circ$", color='green', weight='bold')

            # Puntos fijos A y B
            ax_geom.plot(x_A, y_A, 'ko', markersize=6)
            ax_geom.text(x_A, y_A + 0.3, "A", ha='center')
            ax_geom.plot(x_B, y_B, 'ko', markersize=6)
            ax_geom.text(x_B, y_B - 0.6, "B", ha='center')
            
            ax_geom.set_xlim(-6, 6)
            ax_geom.set_ylim(-6, 6)
            ax_geom.set_aspect('equal')
            ax_geom.axis('off')
            
            st.pyplot(fig_geom)
            
        with sub_col2:
            st.markdown("**Comportamiento del Espacio de Configuración (OPL)**")
            fig_fermat, ax_fermat = plt.subplots(figsize=(6, 5))
            
            ax_fermat.plot(x_array, opl_array, color='blue', linewidth=2, label="$OPL(x)$")
            ax_fermat.plot(x_interfaz, opl_puntual, 'ro', markersize=8, label="Posición Actual")
            ax_fermat.axvline(x_min, color='green', linestyle='--', alpha=0.7, label=f"Mínimo Teórico")
            
            ax_fermat.set_xlabel("Coordenada x en la frontera (cm)")
            ax_fermat.set_ylabel("Camino Óptico Relativo")
            ax_fermat.grid(True, alpha=0.3)
            ax_fermat.legend(loc='upper center')
            
            st.pyplot(fig_fermat)