import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
from utils_math import (vector_jones_inicial, matriz_polarizador_lineal, 
                        matriz_retardador, curva_elipse_polarizacion)

# Configuración de la página web
st.set_page_config(page_title="Módulo V: Polarización", layout="wide")

st.title("Módulo V: Polarización y Formalismo de Jones")
st.markdown("Estudio matricial del estado de polarización de la luz y su modulación por elementos ópticos anisotrópicos.")

# --- FUNCIÓN AUXILIAR (EULER) ---
def jones_a_euler_latex(Jx, Jy):
    """Convierte un vector de Jones complejo a notación de Euler en LaTeX"""
    def formatear_componente(z):
        amp = np.abs(z)
        fase = np.angle(z) # Devuelve la fase de -pi a pi
        
        if amp < 1e-4: 
            return "0"
        if abs(fase) < 1e-4: 
            return f"{amp:.2f}"
            
        return f"{amp:.2f} e^{{{fase:+.2f}i}}"
    
    comp_x = formatear_componente(Jx)
    comp_y = formatear_componente(Jy)
    
    return r"\vec{E}_{salida} = \begin{pmatrix} " + comp_x + r" \\ " + comp_y + r" \end{pmatrix}"


# --- INICIALIZACIÓN DE MEMORIA ---
if 'elementos_polarizacion' not in st.session_state:
    st.session_state.elementos_polarizacion = []

# --- BARRA LATERAL (CONTROLES) ---
st.sidebar.header("1. Fuente de Luz")
estado_inicial = st.sidebar.selectbox("Estado de Polarización Inicial", 
    ['Lineal Horizontal', 'Lineal Vertical', 'Lineal +45°', 'Circular Derecha', 'Circular Izquierda'])

st.sidebar.divider()

st.sidebar.header("2. Agregar Elemento Óptico")
with st.sidebar.form("form_elementos"):
    tipo = st.selectbox("Tipo de Elemento", ["Polarizador Lineal", "Lámina Retardadora"])
    angulo = st.number_input("Ángulo de inclinación (grados)", value=45.0, step=5.0,
                             help="Ángulo del eje de transmisión o eje rápido respecto a la horizontal.")
    
    retardo = 0.0
    if tipo == "Lámina Retardadora":
        tipo_retardo = st.selectbox("Desfase (Retardo)", ["Lámina de Cuarto de Onda (λ/4)", "Lámina de Media Onda (λ/2)", "Personalizado"])
        if tipo_retardo == "Lámina de Cuarto de Onda (λ/4)": retardo = 90.0
        elif tipo_retardo == "Lámina de Media Onda (λ/2)": retardo = 180.0
        else: retardo = st.number_input("Retardo personalizado en grados", value=45.0)

    btn = st.form_submit_button("Añadir al tren óptico")
    if btn:
        st.session_state.elementos_polarizacion.append({
            'tipo': tipo,
            'angulo': angulo,
            'retardo': retardo
        })
        st.rerun()

if st.sidebar.button("🧹 Limpiar Tren Óptico", type="primary"):
    st.session_state.elementos_polarizacion = []
    st.rerun()

# --- MOTOR DE CÁLCULO Y GRÁFICOS ---
col1, col2 = st.columns([1, 2])

# 1. Vector de Jones Inicial (Luz entrante)
E_final = vector_jones_inicial(estado_inicial)

# 2. Propagación secuencial del Campo Eléctrico
# La luz atraviesa los elementos exactamente en el orden en que se añadieron a la lista
for elem in st.session_state.elementos_polarizacion:
    if elem['tipo'] == "Polarizador Lineal":
        M_comp = matriz_polarizador_lineal(elem['angulo'])
    else:
        M_comp = matriz_retardador(elem['angulo'], elem['retardo'])
    
    # El campo es transformado por el elemento óptico actual
    E_final = np.dot(M_comp, E_final)

# 3. Componentes finales e Intensidad
Ex, Ey = E_final[0,0], E_final[1,0]
intensidad = np.abs(Ex)**2 + np.abs(Ey)**2

# ... (el resto de tu código de la interfaz sigue igual a partir de aquí)
with col1:
    st.subheader("Tren de Elementos Ópticos")
    if not st.session_state.elementos_polarizacion:
        st.info("Sin elementos. Visualizando la fuente original.")
    else:
        for i, elem in enumerate(st.session_state.elementos_polarizacion):
            if elem['tipo'] == "Polarizador Lineal":
                st.success(f"**{i+1}. Polarizador** a {elem['angulo']:.1f}°")
            else:
                st.warning(f"**{i+1}. Retardador** a {elem['angulo']:.1f}° (Desfase: {elem['retardo']:.1f}°)")

    st.divider()
    st.subheader("Análisis de Jones")
    st.markdown("Vector del Campo Eléctrico de Salida $\\vec{E}_{out}$:")
    
    st.latex(jones_a_euler_latex(Ex, Ey))    
    st.metric(label="Irradiancia Relativa (I/I₀)", value=f"{intensidad:.4f}")

with col2:
    st.subheader("Elipse de Polarización Transversal")
    
    # Añadimos el botón de animación justo arriba de la gráfica
    animar = st.button("▶ Animar Propagación del Campo")
    
    # Contenedor dinámico de Streamlit para la sobrescritura de fotogramas
    grafica_placeholder = st.empty()
    
    def dibujar_fotograma(t_anim):
        fig, ax = plt.subplots(figsize=(6, 6))
        Ex_t, Ey_t = curva_elipse_polarizacion(Ex, Ey)
        
        ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(0, color='gray', linestyle='--', alpha=0.5)
        
        if intensidad < 1e-4:
            ax.text(0, 0, "Extinción Total\n(Oscuridad)", ha='center', va='center', color='red', fontsize=14, weight='bold')
        else:
            # Trayectoria completa en tono morado suave
            ax.plot(Ex_t, Ey_t, color='purple', linewidth=2.5, alpha=0.3)
            
            # Ajuste de propagación del vector instantáneo considerando amplitudes y fases complejas de forma separada
            x_inst = np.abs(Ex) * np.cos(-t_anim + np.angle(Ex))
            y_inst = np.abs(Ey) * np.cos(-t_anim + np.angle(Ey))
            
            # Dibujamos el nodo giratorio y el vector de campo real
            ax.plot(x_inst, y_inst, 'go', markersize=8)
            ax.arrow(0, 0, x_inst, y_inst, color='green', alpha=0.8, head_width=0.04, length_includes_head=True)
        
        ax.set_xlim(-1.1, 1.1)
        ax.set_ylim(-1.1, 1.1)
        ax.set_aspect('equal')
        ax.set_xlabel("Componente Ex")
        ax.set_ylabel("Componente Ey")
        ax.grid(True, alpha=0.3)
        return fig

    # Lógica de renderizado dinámico / estático
    if animar and intensidad >= 1e-4:
        # Generamos los ángulos para dar dos vueltas completas a la elipse
        fases_t = np.linspace(0, 4 * np.pi, 60) 
        for t in fases_t:
            fig = dibujar_fotograma(t)
            grafica_placeholder.pyplot(fig)
            plt.close(fig) # Liberar memoria de matplotlib
            time.sleep(0.04)
            
        # Al finalizar la animación, se regresa al estado t = 0.0
        fig_final = dibujar_fotograma(0.0)
        grafica_placeholder.pyplot(fig_final)
        plt.close(fig_final)
    else:
        # Modo estático inicial o cambio de estado ordinario
        fig_estatica = dibujar_fotograma(0.0)
        grafica_placeholder.pyplot(fig_estatica)
        plt.close(fig_estatica)