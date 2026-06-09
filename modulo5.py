import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from utils_math import (vector_jones_inicial, matriz_polarizador_lineal, 
                        matriz_retardador, curva_elipse_polarizacion)

st.set_page_config(page_title="Módulo V: Polarización", layout="wide")

st.title("Módulo V: Polarización y Formalismo de Jones")
st.markdown("Estudio matricial del estado de polarización de la luz y su modulación por elementos ópticos anisotrópicos.")

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
    
    # Si es retardador, necesitamos saber el desfase
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

# 1. Cálculo del Vector de Jones Inicial
E_vec = vector_jones_inicial(estado_inicial)
M_sys = np.eye(2, dtype=complex)

# 2. Multiplicación de Matrices (en orden físico: el último elemento se multiplica a la izquierda)
for elem in reversed(st.session_state.elementos_polarizacion):
    if elem['tipo'] == "Polarizador Lineal":
        M_comp = matriz_polarizador_lineal(elem['angulo'])
    else:
        M_comp = matriz_retardador(elem['angulo'], elem['retardo'])
    M_sys = np.dot(M_comp, M_sys)

# 3. Vector de Jones Final y Constantes Físicas
E_final = np.dot(M_sys, E_vec)
Ex, Ey = E_final[0,0], E_final[1,0]
intensidad = np.abs(Ex)**2 + np.abs(Ey)**2

with col1:
    st.subheader("Tren de Elementos Ópticos")
    if not st.session_state.elementos_polarizacion:
        st.info("Sin elementos. Visualizando la fuente original.")
    else:
        for i, elem in enumerate(st.session_state.elementos_polarizacion):
            if elem['tipo'] == "Polarizador Lineal":
                st.success(f"**{i+1}. Polarizador** a {elem['angulo']}°")
            else:
                st.warning(f"**{i+1}. Retardador** a {elem['angulo']}° (Desfase: {elem['retardo']}°)")

    st.divider()
    st.subheader("Análisis de Jones")
    st.markdown("Vector del Campo Eléctrico de Salida $\\vec{E}_{out}$:")
    
    # Formateo de números complejos para renderizado en LaTeX
    Ex_str = f"{np.real(Ex):.2f} {np.imag(Ex):+.2f}i"
    Ey_str = f"{np.real(Ey):.2f} {np.imag(Ey):+.2f}i"
    st.latex(r"\vec{E}_{out} = \begin{pmatrix} " + Ex_str + r" \\ " + Ey_str + r" \end{pmatrix}")
    
    st.metric(label="Irradiancia Relativa (I/I₀)", value=f"{intensidad:.4f}")

with col2:
    st.subheader("Elipse de Polarización Trasversal")
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Extraer la curva paramétrica
    Ex_t, Ey_t = curva_elipse_polarizacion(Ex, Ey)
    
    # Ejes de referencia
    ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(0, color='gray', linestyle='--', alpha=0.5)
    
    if intensidad < 1e-4:
        # Extinción total
        ax.text(0, 0, "Extinción Total\n(Oscuridad)", ha='center', va='center', color='red', fontsize=14, weight='bold')
    else:
        # Graficar la trayectoria del vector de campo eléctrico
        ax.plot(Ex_t, Ey_t, color='purple', linewidth=2.5, label=r'$\vec{E}(t)$')
        # Marcar un punto de referencia para indicar rotación
        ax.plot(Ex_t[0], Ey_t[0], 'go', markersize=8, label='Inicio t=0')
    
    # Configuramos límites fijos estrictos para que el tamaño visual represente la intensidad real
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_aspect('equal') # Crucial para que el círculo no se vea ovalado
    ax.set_xlabel("Componente Ex")
    ax.set_ylabel("Componente Ey")
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')
    
    st.pyplot(fig)