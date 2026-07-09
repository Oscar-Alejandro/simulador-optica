import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Importamos el motor matemático
from utils_math import trazar_rayo_sistema, obtener_matriz_sistema

# --- NUEVA FUNCIÓN PARA CONVENCIÓN VISUAL DE FLECHAS ---
def dibujar_flecha(ax, z, y, tipo="objeto"):
    """Renderiza la flecha del objeto o la imagen respetando convenciones ópticas."""
    if tipo == "objeto":
        color = "green"
        alfa = 1.0
        estilo = "-"
        etiqueta = "Objeto"
    elif tipo == "real":
        color = "darkorange" 
        alfa = 1.0
        estilo = "-"
        etiqueta = "Img. Real"
    elif tipo == "virtual":
        color = "purple"
        alfa = 0.6 
        estilo = "--" 
        etiqueta = "Img. Virtual"
        
    # Dibujar flecha
    ax.annotate('', xy=(z, y), xytext=(z, 0),
                arrowprops=dict(arrowstyle="->", color=color, linewidth=3, alpha=alfa, ls=estilo))
    
    # Colocar etiqueta (se invierte si la imagen está invertida)
    desplazamiento = 0.8 if y > 0 else -0.8
    ax.text(z, y + desplazamiento, etiqueta, color=color, fontsize=10, 
            fontweight='bold', ha='center', va='center', alpha=alfa)


# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Módulo I: Óptica Geométrica", layout="wide")

st.title("Módulo I: Formación de Imágenes y Trazado Paraxial")
st.markdown("Banco óptico virtual para el diseño de sistemas formadores de imágenes.")

if 'componentes' not in st.session_state:
    st.session_state.componentes = []

# --- BARRA LATERAL ---
st.sidebar.header("1. Configuración de la Fuente")

with st.sidebar.form("form_fuente"):
    modo = st.radio("Modo de Emisión", ["Formación de Imagen (Objeto)", "Rayo Único"])

    if modo == "Rayo Único":
        y0 = st.slider("Altura inicial y₀ (cm)", -5.0, 5.0, 1.0, 0.1)
        theta0 = st.slider("Ángulo inicial θ₀ (°)", -15.0, 15.0, 0.0, 0.5)
    else:
        y0 = st.slider("Altura del Objeto (cm)", 0.5, 5.0, 2.5, 0.1)
        
    if len(st.session_state.componentes) > 0:
        st.divider()
        st.markdown("**Posición del Objeto**")
        d1_actual = float(st.session_state.componentes[0][2])
        nuevo_d1 = st.slider("Distancia a la 1ra Lente (cm)", 1.0, 100.0, d1_actual, 1.0,
                             help="Aleja o acerca el objeto del sistema óptico ya construido.")
    else:
        nuevo_d1 = None

    btn_calcular = st.form_submit_button("Calcular / Actualizar")

if btn_calcular and nuevo_d1 is not None:
    tipo, f, d_viejo = st.session_state.componentes[0]
    if nuevo_d1 != d_viejo:
        st.session_state.componentes[0] = (tipo, f, nuevo_d1)
        st.rerun()

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

# --- ÁREA CENTRAL ---
col1, col2 = st.columns([1, 2.3])

with col1:
    st.subheader("Componentes del Sistema")
    if len(st.session_state.componentes) == 0:
        st.info("El banco óptico está vacío. Agrega una lente en el panel izquierdo.")
    else:
        for i, (tipo, f, d) in enumerate(st.session_state.componentes):
            tipo_lente = "Convergente" if f > 0 else "Divergente"
            st.success(f"**Lente {i+1} ({tipo_lente}):**\n- Focal: {f} cm\n- Posición: a {d} cm del anterior")
            
        st.divider()
        st.subheader("Análisis Matriz ABCD")
        
        M_sys = obtener_matriz_sistema(st.session_state.componentes)
        A, B, C, D = M_sys[0,0], M_sys[0,1], M_sys[1,0], M_sys[1,1]
        
        st.latex(r"M_{sys} = \begin{pmatrix}" + f"{A:.4f} & {B:.4f} \\\\ {C:.4f} & {D:.4f}" + r"\end{pmatrix}")
        
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
        dibujar_flecha(ax, 0, y0, tipo="objeto")

    if len(st.session_state.componentes) > 0:
        if modo == "Rayo Único":
            angulos = [theta0]
        else:
            d1 = st.session_state.componentes[0][2]
            ang_central = np.degrees(np.arctan2(-y0, d1)) if d1 > 0 else 0.0
            angulos = [0.0, ang_central, ang_central * 2.0]

        rayos_trazados = []

        for idx, ang in enumerate(angulos):
            z_vals, y_vals, _ = trazar_rayo_sistema(y0, ang, st.session_state.componentes, d_final)
            leyenda = 'Haz de luz' if idx == 0 else None
            ax.plot(z_vals, y_vals, color='red', alpha=0.6, linewidth=1.5, label=leyenda)
            rayos_trazados.append((z_vals, y_vals))
            
        z_acumulado = 0.0
        for i, (tipo, f, d) in enumerate(st.session_state.componentes):
            z_acumulado += d
            color_lente = '#1f77b4' if f > 0 else '#ff7f0e'
            estilo = '-' if f > 0 else '--'
            ax.plot([z_acumulado, z_acumulado], [-8, 8], color=color_lente, linestyle=estilo, linewidth=2)
            ax.text(z_acumulado, 8.2, f"$L_{i+1}$ (f={f})", ha='center', va='bottom', color=color_lente, weight='bold')

        if modo == "Formación de Imagen (Objeto)" and len(rayos_trazados) >= 2:
            z_rayo1, y_rayo1 = rayos_trazados[0]
            z_rayo2, y_rayo2 = rayos_trazados[1]
            
            z_a, z_b = z_rayo1[-2], z_rayo1[-1]
            y1_a, y1_b = y_rayo1[-2], y_rayo1[-1]
            y2_a, y2_b = y_rayo2[-2], y_rayo2[-1]
            
            dz = z_b - z_a
            if dz > 0:
                m1 = (y1_b - y1_a) / dz
                m2 = (y2_b - y2_a) / dz
                
                if abs(m1 - m2) > 1e-5:
                    c1 = y1_b - m1 * z_b
                    c2 = y2_b - m2 * z_b
                    
                    z_imagen = (c2 - c1) / (m1 - m2)
                    y_imagen = m1 * z_imagen + c1
                    
                    if z_imagen < z_acumulado:
                        ax.plot([z_imagen, z_b], [y_imagen, y1_b], color='gray', linestyle='--', linewidth=1.5, alpha=0.5)
                        ax.plot([z_imagen, z_b], [y_imagen, y2_b], color='gray', linestyle='--', linewidth=1.5, alpha=0.5, label='Extensión Virtual')
                        dibujar_flecha(ax, z_imagen, y_imagen, tipo="virtual")
                    else:
                        dibujar_flecha(ax, z_imagen, y_imagen, tipo="real")

        limite_izquierdo = min(-2, z_imagen - 2) if (modo == "Formación de Imagen (Objeto)" and 'z_imagen' in locals() and z_imagen < z_acumulado) else -2
        limite_derecho = max(z_vals) + 5
        if modo == "Formación de Imagen (Objeto)" and 'z_imagen' in locals() and z_imagen >= z_acumulado:
            limite_derecho = max(limite_derecho, z_imagen + 5) 
            
        ax.set_xlim(limite_izquierdo, limite_derecho)
        
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
    if by_label:
        ax.legend(by_label.values(), by_label.keys(), loc='lower left')
    
    st.pyplot(fig)

    # --- NUEVO BLOQUE DE DATOS ANALÍTICOS DE LA IMAGEN ---
    if modo == "Formación de Imagen (Objeto)" and len(st.session_state.componentes) > 0 and 'z_imagen' in locals():
        magnificacion = y_imagen / y0
        tipo_imagen = "Virtual" if z_imagen < z_acumulado else "Real"
        
        st.info(f"📊 **Datos Analíticos de la Imagen ({tipo_imagen}):** \n"
                f"**Posición (z):** {z_imagen:.2f} cm | "
                f"**Altura (y):** {y_imagen:.2f} cm | "
                f"**Magnificación (m):** {magnificacion:.2f}X")