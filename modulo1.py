import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from utils_math import trazar_rayo_sistema, obtener_matriz_sistema

# Configuración de la página web
st.set_page_config(page_title="Módulo I: Óptica Geométrica", layout="wide")

st.title("Módulo I: Formación de Imágenes y Trazado Paraxial")
st.markdown("Banco óptico virtual para el diseño de sistemas formadores de imágenes.")

# --- INICIALIZACIÓN DEL ESTADO DE MEMORIA ---
if 'componentes' not in st.session_state:
    st.session_state.componentes = []

# --- BARRA LATERAL (CONTROLES) ---
st.sidebar.header("1. Configuración de la Fuente")
modo = st.sidebar.radio("Modo de Emisión", ["Formación de Imagen (Objeto)", "Rayo Único"])

if modo == "Rayo Único":
    y0 = st.sidebar.slider("Altura inicial y₀ (cm)", -5.0, 5.0, 1.0, 0.1)
    theta0 = st.sidebar.slider("Ángulo inicial θ₀ (°)", -15.0, 15.0, 0.0, 0.5)
else:
    y0 = st.sidebar.slider("Altura del Objeto (cm)", 0.5, 5.0, 2.5, 0.1)

st.sidebar.divider()

st.sidebar.header("2. Agregar Componente Óptico")
with st.sidebar.form("form_agregar"):
    focal_input = st.number_input("Distancia Focal f (cm)", value=10.0, step=1.0)
    distancia_input = st.number_input("Distancia desde el elemento anterior (cm)", value=15.0, min_value=0.0, step=1.0)
    
    btn_agregar = st.form_submit_button("Añadir Lente al Sistema")
    if btn_agregar:
        st.session_state.componentes.append(('lente', focal_input, distancia_input))
        st.rerun()

if st.sidebar.button("🧹 Limpiar Banco Óptico", type="primary"):
    st.session_state.componentes = []
    st.rerun()

st.sidebar.divider()

st.sidebar.header("3. Pantalla de Proyección")
d_final = st.sidebar.slider("Distancia de propagación extra (cm)", 10.0, 100.0, 40.0, 5.0)

# --- MOTOR DE CÁLCULO Y GRÁFICOS ---
col1, col2 = st.columns([1, 2.3])

with col1:
    st.subheader("Componentes del Sistema")
    if len(st.session_state.componentes) == 0:
        st.info("El banco óptico está vacío. Agrega una lente en el panel izquierdo.")
    else:
        for i, (tipo, f, d) in enumerate(st.session_state.componentes):
            tipo_lente = "Convergente" if f > 0 else "Divergente"
            st.success(f"**Lente {i+1} ({tipo_lente}):**\n- Focal: {f} cm\n- Posición: a {d} cm del anterior")
            
        # --- BLOQUE ANALÍTICO: MATRIZ EQUIVALENTE ---
        st.divider()
        st.subheader("Análisis Matriz ABCD")
        
        M_sys = obtener_matriz_sistema(st.session_state.componentes)
        A, B, C, D = M_sys[0,0], M_sys[0,1], M_sys[1,0], M_sys[1,1]
        
        # Renderizado de la matriz estilo libro de texto
        st.latex(r"M_{sys} = \begin{pmatrix}" + f"{A:.4f} & {B:.4f} \\\\ {C:.4f} & {D:.4f}" + r"\end{pmatrix}")
        
        # Deducción de constantes físicas globales
        if C != 0:
            f_eq = -1.0 / C
            h1 = (D - 1.0) / C
            h2 = (A - 1.0) / C
            
            st.metric(label="Distancia Focal Equivalente ($f_{eq}$)", value=f"{f_eq:.2f} cm")
            with st.expander("Ver Planos Principales"):
                st.write(f"• **Plano Principal Principal ($h_1$):** {h1:.2f} cm (desde el inicio)")
                st.write(f"• **Plano Principal de Salida ($h_2$):** {h2:.2f} cm (desde la última lente)")
        else:
            st.warning("Sistema Afocal (Focal equivalente infinita). Las lentes están configuradas como un telescopio colimador.")

with col2:
    st.subheader("Simulación del Trazado de Rayos")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axhline(0, color='black', linestyle='-.', alpha=0.6, label='Eje Óptico')
    
    if modo == "Formación de Imagen (Objeto)":
        ax.arrow(0, 0, 0, y0, head_width=0.4, head_length=0.6, fc='green', ec='green', 
                 length_includes_head=True, width=0.08, label='Objeto')

    if len(st.session_state.componentes) > 0:
        if modo == "Rayo Único":
            angulos = [theta0]
        else:
            d1 = st.session_state.componentes[0][2]
            ang_central = np.degrees(np.arctan2(-y0, d1)) if d1 > 0 else 0.0
            angulos = [0.0, ang_central, ang_central * 2.0]

        for idx, ang in enumerate(angulos):
            z_vals, y_vals, _ = trazar_rayo_sistema(y0, ang, st.session_state.componentes, d_final)
            leyenda = 'Haz de luz' if idx == 0 else None
            ax.plot(z_vals, y_vals, color='red', alpha=0.6, linewidth=1.5, label=leyenda)
            
        z_acumulado = 0.0
        for i, (tipo, f, d) in enumerate(st.session_state.componentes):
            z_acumulado += d
            color_lente = '#1f77b4' if f > 0 else '#ff7f0e'
            estilo = '-' if f > 0 else '--'
            ax.plot([z_acumulado, z_acumulado], [-8, 8], color=color_lente, linestyle=estilo, linewidth=2)
            ax.text(z_acumulado, 8.2, f"$L_{i+1}$ (f={f})", ha='center', va='bottom', color=color_lente, weight='bold')

        ax.set_xlim(-2, max(z_vals) + 5)
    else:
        z_fin = d_final
        ang_rad = np.radians(theta0 if modo == "Rayo Único" else 0.0)
        y_fin = y0 + z_fin * np.tan(ang_rad)
        ax.plot([0, z_fin], [y0, y_fin], color='red', alpha=0.6, linewidth=1.5, label='Rayo')
        ax.set_xlim(-2, d_final + 5)

    ax.set_ylim(-10, 10)
    ax.set_xlabel('Distancia a lo largo del eje óptico Z (cm)')
    ax.set_ylabel('Altura Y (cm)')
    ax.grid(True, alpha=0.3)
    
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='lower left')
    
    st.pyplot(fig)