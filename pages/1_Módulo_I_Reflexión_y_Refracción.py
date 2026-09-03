import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from utils_math import calcular_snell, analizar_camino_optico, calcular_fresnel

# Configuración de la página web
st.set_page_config(page_title="Módulo I: Reflexión y Refracción", layout="wide")

st.title("Módulo I: Reflexión y Refracción")
st.markdown("Estudio de la Ley de Snell y verificación del Principio de Fermat.")

# --- BARRA LATERAL (CONTROLES) ---
st.sidebar.header("Parámetros del Sistema (Snell)")
n1 = st.sidebar.slider("Índice de refracción (Medio 1)", 1.0, 3.0, 1.0, 0.01)
# Restricción: n2 siempre será mayor o igual a n1 para evitar Reflexión Total Interna
n2 = st.sidebar.slider("Índice de refracción (Medio 2)", float(n1), 3.0, max(1.5, float(n1)), 0.01)
theta_i_deg = st.sidebar.slider("Ángulo de Incidencia θ₁ (°)", 0.00, 89.99, 45.00, 0.01)
st.sidebar.divider()

st.sidebar.header("Principio de Fermat")
st.sidebar.markdown("Encuentra la trayectoria real minimizando el camino óptico entre A y B.")
# 2. Ajustar los límites del deslizador para que barra exclusivamente desde A hasta B
x_interfaz = st.sidebar.slider("Desliza el punto de incidencia 'x' en la frontera", 
                               min_value=0.0, max_value=8.0, value=4.0, step=0.1)
# --- CÁLCULOS MATEMÁTICOS BÁSICOS ---
theta_t_deg, tir, theta_critico = calcular_snell(n1, n2, theta_i_deg)

# 1. Fijar la proyección del punto A en x=0 y mover B a una distancia 'd' (ej. d = 8.0)
x_A, y_A = 0.0, 4.0
x_B, y_B = 8.0, -4.0

opl_puntual, x_array, opl_array, x_min, opl_min = analizar_camino_optico(
    n1, n2, x_A, y_A, x_B, y_B, x_interfaz
)

# --- MOTOR DE GRÁFICOS Y CONTENEDORES ---
col1, col2 = st.columns([1, 2.5])

with col1:
    st.subheader("Fundamento Teórico")
    st.markdown("La Ley de Snell describe la refracción geométrica en la frontera:")
    st.latex(r"n_1 \sin(\theta_i) = n_2 \sin(\theta_t)")
    
    st.success(f"**Ángulo de Refracción:** {theta_t_deg:.2f}°")

    st.divider()
    
    # --- ANÁLISIS DE ENERGÍA CON COMPONENTES S Y P ---
    st.subheader("Análisis de Energía (Fresnel)")
    Rs, Rp, R_main, Ts, Tp, T_main = calcular_fresnel(n1, n2, theta_i_deg)
    
    st.markdown("**Luz no polarizada (Promedio):**")
    met1, met2 = st.columns(2)
    met1.metric(label="Reflectancia (R)", value=f"{R_main*100:.1f} %")
    met2.metric(label="Transmitancia (T)", value=f"{T_main*100:.1f} %")
    
    st.markdown("**Componentes de Polarización:**")
    # Primera fila: Reflectancias
    c1, c2 = st.columns(2)
    c1.metric("R_s", f"{Rs*100:.1f} %")
    c2.metric("R_p", f"{Rp*100:.1f} %")
    
    # Segunda fila: Transmitancias
    c3, c4 = st.columns(2)
    c3.metric("T_s", f"{Ts*100:.1f} %")
    c4.metric("T_p", f"{Tp*100:.1f} %")
    
    # Alerta didáctica para el Ángulo de Brewster
    if Rp < 0.001 and theta_i_deg > 0:
        st.info("💡 **¡Ángulo de Brewster detectado!** La componente paralela ($p$) se transmite por completo y la luz reflejada queda 100% polarizada en $s$.")
    
    st.divider()
    
    st.subheader("Principio de Fermat")
    st.markdown("Establece que la luz sigue la trayectoria que minimiza el tiempo de viaje o **Camino Óptico (LCO)**:")
    st.latex(r"LCO(x) = n_1 L_1 + n_2 L_2")
    
    st.metric(label="Camino Óptico Actual", value=f"{opl_puntual:.4f}")
    st.metric(label="Mínimo Absoluto (Fermat)", value=f"{opl_min:.4f}")
    
if abs(x_interfaz - x_min) < 0.15:
    st.success(f"¡Trayectoria Real! x ≈ {x_min:.2f} cm — "
               f"este punto minimiza el LCO y cumple la Ley de Snell.")
else:
    diferencia = opl_puntual - opl_min
    st.warning(f"Trayectoria de prueba — el LCO actual excede al mínimo "
               f"en {diferencia:.4f} unidades. "
               f"Mueva el deslizador hacia x ≈ {x_min:.2f} cm para "
               f"encontrar la trayectoria que la naturaleza elige.")

with col2:
    # --- 2 PESTAÑAS PARALELAS ---
    tab1, tab2 = st.tabs(["1. Trazado de Rayos (Snell)", "2. Minimización (Fermat)"])
    
    with tab1:
        st.subheader("Visualización Geométrica de la Ley de Snell")
        fig_snell, ax_snell = plt.subplots(figsize=(8, 5))
        
        # Frontera y Normal
        ax_snell.axhline(0, color='black', linewidth=2)
        ax_snell.axvline(0, color='gray', linestyle=':', alpha=0.6)
        
        # Fondos de los medios
        ax_snell.fill_between([-5, 5], 0, 5, color='blue', alpha=0.03)
        ax_snell.fill_between([-5, 5], -5, 0, color='green', alpha=0.03)
        
        ax_snell.text(0.02, 0.92, f"Medio 1 (n₁ = {n1})", transform=ax_snell.transAxes, weight='bold', fontsize=10)
        ax_snell.text(0.02, 0.05, f"Medio 2 (n₂ = {n2})", transform=ax_snell.transAxes, weight='bold', fontsize=10)
        
        rad_i = np.radians(theta_i_deg)
        x_inc = -np.sin(rad_i) * 4.5
        y_inc = np.cos(rad_i) * 4.5
        
        c_inc_text = "#8B0000"    
        c_ref_text = "#A04000"    
        c_trans_text = "#004D20"  
        
        # 1. Rayo Incidente
        ax_snell.plot([x_inc, 0], [y_inc, 0], color='red', linewidth=3, 
                      label=f"Incidente ($\\theta_i = {theta_i_deg:.1f}^\\circ$)")
        
        # 2. Rayo Reflejado
        grosor_ref = max(1.0, 4.0 * R_main)
        alpha_ref = max(0.3, R_main)
        ax_snell.plot([0, -x_inc], [0, y_inc], color='orange', linewidth=grosor_ref, alpha=alpha_ref, linestyle='--', 
                      label=f"Reflejado ($R = {R_main*100:.1f}\%$, $\\theta_r = {theta_i_deg:.1f}^\\circ$)")
        ax_snell.text(-x_inc/2 - 0.8, y_inc/2 + 0.3, f"R = {R_main*100:.1f}%", color=c_ref_text, weight='bold')
        
        r_arc = 1.2  
        t_arc_i = np.linspace(0, rad_i, 20)
        
        ax_snell.plot(-r_arc * np.sin(t_arc_i), r_arc * np.cos(t_arc_i), color='red', lw=1.2)
        ax_snell.text(-1.4 * r_arc * np.sin(rad_i/2), 1.4 * r_arc * np.cos(rad_i/2), 
                      r"$\theta_i$", color=c_inc_text, fontsize=11, ha='center', va='center', weight='bold')
        
        ax_snell.plot(r_arc * np.sin(t_arc_i), r_arc * np.cos(t_arc_i), color='orange', lw=1.2)
        ax_snell.text(1.4 * r_arc * np.sin(rad_i/2), 1.4 * r_arc * np.cos(rad_i/2), 
                      r"$\theta_r$", color=c_ref_text, fontsize=11, ha='center', va='center', weight='bold')
        
        # 3. Rayo Refractado (Siempre ocurre porque n1 <= n2)
        rad_t = np.radians(theta_t_deg)
        x_ref = np.sin(rad_t) * 4.5
        y_ref = -np.cos(rad_t) * 4.5
        
        grosor_trans = max(1.0, 4.0 * T_main)
        alpha_trans = max(0.3, T_main)
        ax_snell.plot([0, x_ref], [0, y_ref], color='green', linewidth=grosor_trans, alpha=alpha_trans, 
                      label=f"Refractado ($T = {T_main*100:.1f}\%$, $\\theta_t = {theta_t_deg:.1f}^\\circ$)")
        ax_snell.text(x_ref/2 + 0.2, y_ref/2 - 0.5, f"T = {T_main*100:.1f}%", color=c_trans_text, weight='bold')
        
        t_arc_t = np.linspace(0, rad_t, 20)
        ax_snell.plot(r_arc * np.sin(t_arc_t), -r_arc * np.cos(t_arc_t), color='green', lw=1.2)
        ax_snell.text(1.4 * r_arc * np.sin(rad_t/2), -1.4 * r_arc * np.cos(rad_t/2), 
                      r"$\theta_t$", color=c_trans_text, fontsize=11, ha='center', va='center', weight='bold')
            
        ax_snell.set_xlim(-5, 5)
        ax_snell.set_ylim(-5, 5)
        ax_snell.set_aspect('equal')
        ax_snell.axis('off')
        
        ax_snell.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3, fontsize=9.5, framealpha=0.95)
        
        st.pyplot(fig_snell)

    with tab2:
        st.subheader("Análisis de Trayectorias Variacionales")
        sub_col1, sub_col2 = st.columns(2)
        
        with sub_col1:
            st.markdown("**Camino Geométrico de Prueba**")
            fig_geom, ax_geom = plt.subplots(figsize=(6, 5))
            
            ax_geom.axhline(0, color='black', linewidth=1.5)
            ax_geom.axvline(x_interfaz, color='gray', linestyle='-.', alpha=0.6)
            
            vec_inc = np.array([x_interfaz - x_A, 0 - y_A])
            ang_inc_rad = np.arctan(abs(vec_inc[0]) / abs(vec_inc[1])) 
            
            vec_trans = np.array([x_B - x_interfaz, y_B - 0])
            ang_trans_rad = np.arctan(abs(vec_trans[0]) / abs(vec_trans[1]))
            
            Rs_test, Rp_test, R_test, Ts_test, Tp_test, T_test = calcular_fresnel(n1, n2, np.degrees(ang_inc_rad))
            grosor_base = 4.0
            
            ax_geom.plot([x_A, x_interfaz], [y_A, 0], color='red', linewidth=grosor_base, label="Incidente")
            
            x_refl = x_interfaz + (x_interfaz - x_A)
            ax_geom.plot([x_interfaz, x_refl], [0, y_A], color='orange', linestyle='--', linewidth=max(1.0, grosor_base * R_test), alpha=max(0.3, R_test))
            ax_geom.text((x_interfaz + x_refl)/2 - 0.8, y_A/2 + 0.3, f"R = {R_test*100:.1f}%", color='orange', weight='bold')
            
            if T_test > 0:
                ax_geom.plot([x_interfaz, x_B], [0, y_B], color='green', linewidth=max(1.0, grosor_base * T_test), label="Transmitido")
                ax_geom.text((x_interfaz + x_B)/2 + 0.2, y_B/2 - 0.5, f"T = {T_test*100:.1f}%", color='green', weight='bold')
            
            r_arc = 1.0 
            ang_normal_up = np.pi/2
            ang_vec_inc = np.arctan2(-vec_inc[1], -vec_inc[0]) 
            t_arc_i = np.linspace(ang_normal_up, ang_vec_inc, 20)
            ax_geom.plot(x_interfaz + r_arc*np.cos(t_arc_i), r_arc*np.sin(t_arc_i), color='red', lw=1.5)
            ax_geom.text(x_interfaz + 1.3*r_arc*np.cos((ang_normal_up+ang_vec_inc)/2), 
                         1.3*r_arc*np.sin((ang_normal_up+ang_vec_inc)/2), 
                         f"$\\theta_i = {np.degrees(ang_inc_rad):.1f}^\\circ$", color='red', weight='bold')

            ang_normal_down = -np.pi/2
            ang_vec_trans = np.arctan2(vec_trans[1], vec_trans[0])
            t_arc_t = np.linspace(ang_normal_down, ang_vec_trans, 20)
            if T_test > 0:
                ax_geom.plot(x_interfaz + r_arc*np.cos(t_arc_t), r_arc*np.sin(t_arc_t), color='green', lw=1.5)
                ax_geom.text(x_interfaz + 1.3*r_arc*np.cos((ang_normal_down+ang_vec_trans)/2), 
                             1.3*r_arc*np.sin((ang_normal_down+ang_vec_trans)/2), 
                             f"$\\theta_t = {np.degrees(ang_trans_rad):.1f}^\\circ$", color='green', weight='bold')

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
            st.markdown("**Comportamiento del Espacio de Configuración (LCO)**")
            fig_fermat, ax_fermat = plt.subplots(figsize=(6, 5))
            
            ax_fermat.plot(x_array, opl_array, color='blue', linewidth=2, label="$LCO(x)$")
            ax_fermat.plot(x_interfaz, opl_puntual, 'ro', markersize=8, label="Posición Actual")
            ax_fermat.axvline(x_min, color='green', linestyle='--', alpha=0.7, label=f"Mínimo Teórico")
            
            ax_fermat.set_xlabel("Coordenada x en la frontera (cm)")
            ax_fermat.set_ylabel("Camino Óptico Relativo")
            ax_fermat.grid(True, alpha=0.3)
            ax_fermat.legend(loc='upper center')
            
            st.pyplot(fig_fermat)
            st.info("💡 **Nota didáctica:** En este módulo de Fermat, los puntos A y B están fijos en el espacio. El ángulo de incidencia se calcula geométricamente según la posición de 'x', por lo que es independiente del ángulo definido en la barra lateral para el cálculo de Snell/Fresnel.")