import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from utils_math import calcular_snell, analizar_camino_optico, calcular_fresnel

# Configuración de la página web
st.set_page_config(page_title="Módulo II: Reflexión y Refracción", layout="wide")

st.title("Módulo II: Reflexión y Refracción")
st.markdown("Estudio de la Ley de Snell, verificación del Principio de Fermat y aplicaciones en Guías de Onda.")

# --- BARRA LATERAL (CONTROLES) ---
st.sidebar.header("Parámetros del Sistema (Snell)")
n1 = st.sidebar.slider("Índice de refracción (Medio 1 / Núcleo)", 1.0, 3.0, 1.5, 0.01)
n2 = st.sidebar.slider("Índice de refracción (Medio 2 / Revestimiento)", 1.0, 3.0, 1.3, 0.01)
theta_i_deg = st.sidebar.slider("Ángulo de Incidencia θ₁ (°)", 0.00, 89.99, 75.00, 0.01)
st.sidebar.divider()

st.sidebar.header("Principio de Fermat")
st.sidebar.markdown("Encuentra la trayectoria real minimizando el camino óptico entre A y B.")
x_interfaz = st.sidebar.slider("Desliza el punto de incidencia 'x' en la frontera", 
                               min_value=-5.0, max_value=5.0, value=0.0, step=0.1)

# --- CÁLCULOS MATEMÁTICOS BÁSICOS ---
theta_t_deg, tir, theta_critico = calcular_snell(n1, n2, theta_i_deg)

x_A, y_A = -4.0, 4.0
x_B, y_B = 4.0, -4.0

opl_puntual, x_array, opl_array, x_min, opl_min = analizar_camino_optico(
    n1, n2, x_A, y_A, x_B, y_B, x_interfaz
)

# --- MOTOR DE GRÁFICOS Y CONTENEDORES ---
col1, col2 = st.columns([1, 2.5])

with col1:
    st.subheader("Fundamento Teórico")
    st.markdown("La Ley de Snell describe la refracción geométrica en la frontera:")
    st.latex(r"n_1 \sin(\theta_i) = n_2 \sin(\theta_t)")
    
    if tir:
        st.error(f"**Reflexión Total Interna (TIR)**\nEl ángulo crítico es {theta_critico:.2f}°.")
    else:
        st.success(f"**Ángulo de Refracción:** {theta_t_deg:.2f}°")
        if theta_critico:
            st.info(f"Ángulo crítico del sistema: {theta_critico:.2f}°")

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
    if Rp < 0.001 and not tir and theta_i_deg > 0:
        st.info("💡 **¡Ángulo de Brewster detectado!** La componente paralela ($p$) se transmite por completo y la luz reflejada queda 100% polarizada en $s$.")
    
    st.divider()
    
    st.subheader("Principio de Fermat")
    st.markdown("Establece que la luz sigue la trayectoria que minimiza el tiempo de viaje o **Camino Óptico (OPL)**:")
    st.latex(r"OPL(x) = n_1 L_1 + n_2 L_2")
    
    st.metric(label="Camino Óptico Actual", value=f"{opl_puntual:.4f}")
    st.metric(label="Mínimo Absoluto (Fermat)", value=f"{opl_min:.4f}")
    
    # En modulo2.py, reemplaza el st.warning actual
if abs(x_interfaz - x_min) < 0.15:
    st.success(f"¡Trayectoria Real! x ≈ {x_min:.2f} cm — "
               f"este punto minimiza el OPL y cumple la Ley de Snell.")
else:
    diferencia = opl_puntual - opl_min
    st.warning(f"Trayectoria de prueba — el OPL actual excede al mínimo "
               f"en {diferencia:.4f} unidades. "
               f"Mueva el deslizador hacia x ≈ {x_min:.2f} cm para "
               f"encontrar la trayectoria que la naturaleza elige.")

with col2:
    # --- 3 PESTAÑAS PARALELAS (INCLUYENDO FIBRA ÓPTICA) ---
    tab1, tab2, tab3 = st.tabs(["1. Trazado de Rayos (Snell)", "2. Minimización (Fermat)", "3. Guía de Onda (Fibra Óptica)"])
    
    with tab1:
        st.subheader("Visualización Geométrica de la Ley de Snell")
        fig_snell, ax_snell = plt.subplots(figsize=(8, 5))
        
        # Frontera y Normal
        ax_snell.axhline(0, color='black', linewidth=2)
        ax_snell.axvline(0, color='gray', linestyle=':', alpha=0.6)
        
        # Fondos de los medios
        ax_snell.fill_between([-5, 5], 0, 5, color='blue', alpha=0.03)
        ax_snell.fill_between([-5, 5], -5, 0, color='green', alpha=0.03)
        
        # MEJORA 1: Coordenadas absolutas del eje para fijar las etiquetas en las esquinas izquierdas
        ax_snell.text(0.02, 0.92, f"Medio 1 (n₁ = {n1})", transform=ax_snell.transAxes, weight='bold', fontsize=10)
        ax_snell.text(0.02, 0.05, f"Medio 2 (n₂ = {n2})", transform=ax_snell.transAxes, weight='bold', fontsize=10)
        
        rad_i = np.radians(theta_i_deg)
        x_inc = -np.sin(rad_i) * 4.5
        y_inc = np.cos(rad_i) * 4.5
        
        # Paleta de colores oscuros para texto y símbolos
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
        
        # Símbolos limpios para los arcos
        r_arc = 1.2  
        t_arc_i = np.linspace(0, rad_i, 20)
        
        ax_snell.plot(-r_arc * np.sin(t_arc_i), r_arc * np.cos(t_arc_i), color='red', lw=1.2)
        ax_snell.text(-1.4 * r_arc * np.sin(rad_i/2), 1.4 * r_arc * np.cos(rad_i/2), 
                      r"$\theta_i$", color=c_inc_text, fontsize=11, ha='center', va='center', weight='bold')
        
        ax_snell.plot(r_arc * np.sin(t_arc_i), r_arc * np.cos(t_arc_i), color='orange', lw=1.2)
        ax_snell.text(1.4 * r_arc * np.sin(rad_i/2), 1.4 * r_arc * np.cos(rad_i/2), 
                      r"$\theta_r$", color=c_ref_text, fontsize=11, ha='center', va='center', weight='bold')
        
        # 3. Rayo Refractado
        if not tir:
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
        
        # MEJORA 2: Mover la leyenda abajo de la gráfica en forma horizontal (ncol=3) para liberar el lienzo por completo
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
            
            # --- CORRECCIÓN AQUÍ: Usamos utils_math y convertimos a grados ---
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

    with tab3:
        st.subheader("Aplicación Industrial: Confinamiento en Fibra Óptica")
        st.markdown("Visualiza la propagación de una señal dentro de una guía de onda dieléctrica.")
        
        if n1 <= n2:
            st.warning("⚠️ **Pérdida de señal:** Para que exista confinamiento total, el índice del núcleo (Medio 1) debe ser estrictamente mayor al índice del revestimiento (Medio 2).")
        
        fig_fibra, ax_fibra = plt.subplots(figsize=(10, 3))
        
        ax_fibra.axhline(1, color='black', linewidth=2)
        ax_fibra.axhline(-1, color='black', linewidth=2)
        ax_fibra.fill_between([-1, 20], -1, 1, color='#add8e6', alpha=0.5, label=f"Núcleo (n₁={n1})")
        ax_fibra.fill_between([-1, 20], 1, 2.5, color='gray', alpha=0.2, label=f"Revestimiento (n₂={n2})")
        ax_fibra.fill_between([-1, 20], -2.5, -1, color='gray', alpha=0.2)
        
        x_curr, y_curr = 0.0, 0.0
        dir_y = 1
        ray_x, ray_y = [x_curr], [y_curr]
        max_rebotes = 15
        
        for _ in range(max_rebotes):
            dist_y = 1.0 if y_curr == 0.0 else 2.0
            dx = dist_y * np.tan(np.radians(theta_i_deg))
            
            next_x = x_curr + dx
            next_y = 1.0 if dir_y == 1 else -1.0
            
            t_t, tir_fibra, _ = calcular_snell(n1, n2, theta_i_deg)
            
            if tir_fibra:
                ray_x.append(next_x)
                ray_y.append(next_y)
                x_curr, y_curr = next_x, next_y
                dir_y *= -1
            else:
                ray_x.append(next_x)
                ray_y.append(next_y)
                
                escape_dx = 1.5 * np.tan(np.radians(t_t))
                ax_fibra.plot([next_x, next_x + escape_dx], [next_y, next_y + dir_y * 1.5], 
                              color='red', linestyle='--', linewidth=2, label="Pérdida por refracción")
                break
                
        ax_fibra.plot(ray_x, ray_y, color='blue', linewidth=2.5, label="Señal del haz")
        
        ax_fibra.set_xlim(-0.5, 12)
        ax_fibra.set_ylim(-2.5, 2.5)
        ax_fibra.axis('off')
        
        handles, labels = ax_fibra.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax_fibra.legend(by_label.values(), by_label.keys(), loc='upper right')
        
        st.pyplot(fig_fibra)