import numpy as np

# ==========================================
# MÓDULO II: REFLEXIÓN, REFRACCIÓN Y FRESNEL
# ==========================================

def calcular_snell(n1, n2, theta_i_deg):
    """
    Calcula el ángulo de refracción utilizando la Ley de Snell.
    Retorna el ángulo refractado en grados, un booleano para TIR, 
    y el ángulo crítico (si existe).
    """
    theta_i_rad = np.radians(theta_i_deg)
    sin_theta_t = (n1 / n2) * np.sin(theta_i_rad)
    
    # Cálculo del ángulo crítico (solo de medio denso a menos denso)
    theta_critico = np.degrees(np.arcsin(n2 / n1)) if n1 > n2 else None
    
    # Verificación de Reflexión Total Interna (TIR)
    if sin_theta_t > 1.0:
        return None, True, theta_critico
        
    theta_t_deg = np.degrees(np.arcsin(sin_theta_t))
    return theta_t_deg, False, theta_critico

def calcular_fresnel(n1, n2, theta_i_deg):
    """
    Calcula los coeficientes de reflectancia (R) y transmitancia (T)
    para las componentes s, p, y el promedio para luz no polarizada.
    Recibe el ángulo de incidencia en grados.
    """
    theta_i_rad = np.radians(theta_i_deg)
    sin_theta_t = (n1 / n2) * np.sin(theta_i_rad)
    
    # Caso 1: Reflexión Total Interna (TIR)
    if sin_theta_t >= 1.0:
        return 1.0, 1.0, 1.0, 0.0, 0.0, 0.0

    theta_t_rad = np.arcsin(sin_theta_t)
    
    # Caso 2: Incidencia normal estricta para evitar indeterminaciones 0/0
    if theta_i_deg == 0.0:
        R_normal = ((n1 - n2) / (n1 + n2))**2
        return R_normal, R_normal, R_normal, 1.0 - R_normal, 1.0 - R_normal, 1.0 - R_normal

    cos_i = np.cos(theta_i_rad)
    cos_t = np.cos(theta_t_rad)

    # Coeficientes de reflexión en amplitud y potencia (Polarización s)
    r_s = (n1 * cos_i - n2 * cos_t) / (n1 * cos_i + n2 * cos_t)
    R_s = r_s**2
    T_s = 1.0 - R_s

    # Coeficientes de reflexión en amplitud y potencia (Polarización p)
    r_p = (n1 * cos_t - n2 * cos_i) / (n1 * cos_t + n2 * cos_i)
    R_p = r_p**2
    T_p = 1.0 - R_p

    # Promedios para luz no polarizada (útil para el Módulo II general)
    R_prom = (R_s + R_p) / 2.0
    T_prom = 1.0 - R_prom

    return R_s, R_p, R_prom, T_s, T_p, T_prom

def analizar_camino_optico(n1, n2, x_A, y_A, x_B, y_B, x_interfaz, resolucion=200):
    """
    Calcula el Camino Óptico (OPL) puntual para un x_interfaz arbitrario
    y genera la curva continua para demostrar el principio variacional de Fermat.
    """
    L1_puntual = np.sqrt((x_interfaz - x_A)**2 + y_A**2)
    L2_puntual = np.sqrt((x_B - x_interfaz)**2 + y_B**2)
    opl_puntual = n1 * L1_puntual + n2 * L2_puntual
    
    x_array = np.linspace(x_A - 2, x_B + 2, resolucion)
    L1_array = np.sqrt((x_array - x_A)**2 + y_A**2)
    L2_array = np.sqrt((x_B - x_array)**2 + y_B**2)
    opl_array = n1 * L1_array + n2 * L2_array
    
    indice_min = np.argmin(opl_array)
    x_min = x_array[indice_min]
    opl_min = opl_array[indice_min]
    
    return opl_puntual, x_array, opl_array, x_min, opl_min

# ==========================================
# MÓDULO I: ÓPTICA GEOMÉTRICA (MATRICES ABCD)
# ==========================================

def matriz_translacion(d):
    """Matriz de propagación en el espacio libre por una distancia d."""
    return np.array([[1.0, float(d)], [0.0, 1.0]])

def matriz_lente_delgada(f):
    """Matriz de transformación para una lente delgada de distancia focal f."""
    if f == 0:
        f = 1e-9  # Pequeña perturbación para evitar singularidad numérica
    return np.array([[1.0, 0.0], [-1.0 / float(f), 1.0]])

def matriz_espejo_esferico(R):
    """Matriz de transformación para un espejo esférico de radio R."""
    if R == 0:
        R = 1e-9
    return np.array([[1.0, 0.0], [-2.0 / float(R), 1.0]])

def trazar_rayo_sistema(y0, theta0_deg, componentes, d_final=20.0):
    """Traza las coordenadas transversales de un rayo a lo largo de un eje óptico desplegado."""
    theta0_rad = np.radians(theta0_deg)
    rayo_actual = np.array([[y0], [theta0_rad]])
    
    posiciones_z = [0.0]
    alturas_y = [y0]
    z_actual = 0.0
    
    for tipo, valor, d in componentes:
        if d > 0:
            M_trans = matriz_translacion(d)
            rayo_actual = np.dot(M_trans, rayo_actual)
            z_actual += d
            posiciones_z.append(z_actual)
            alturas_y.append(rayo_actual[0, 0])
            
        if tipo == 'lente':
            M_comp = matriz_lente_delgada(valor)
        elif tipo == 'espejo':
            M_comp = matriz_espejo_esferico(valor)
        else:
            continue
            
        rayo_actual = np.dot(M_comp, rayo_actual)
        
    if len(componentes) > 0:
        M_trans_final = matriz_translacion(d_final)
        rayo_actual = np.dot(M_trans_final, rayo_actual)
        z_actual += d_final
        posiciones_z.append(z_actual)
        alturas_y.append(rayo_actual[0, 0])
        
    return posiciones_z, alturas_y, rayo_actual

def obtener_matriz_sistema(componentes):
    """Calcula la composición multiplicativa analítica del sistema completo."""
    M_acumulada = np.eye(2)
    for tipo, valor, d in componentes:
        if d > 0:
            M_acumulada = np.dot(matriz_translacion(d), M_acumulada)
        if tipo == 'lente':
            M_comp = matriz_lente_delgada(valor)
        elif tipo == 'espejo':
            M_comp = matriz_espejo_esferico(valor)
        else:
            continue
        M_acumulada = np.dot(M_comp, M_acumulada)
    return M_acumulada

# ==========================================
# MÓDULO III: INTERFERENCIA
# ==========================================

def calcular_patron_young(longitud_onda_nm, d_mm, L_cm, tamano_pantalla_cm, resolucion=500):
    """Calcula el patrón de irradiancia bidimensional exacto no paraxial para Young."""
    lam = float(longitud_onda_nm) * 1e-9
    d = float(d_mm) * 1e-3
    L = float(L_cm) * 1e-2
    tamano = float(tamano_pantalla_cm) * 1e-2
    
    x = np.linspace(-tamano/2, tamano/2, resolucion)
    y = np.linspace(-tamano/2, tamano/2, resolucion)
    X, Y = np.meshgrid(x, y)
    
    k = 2.0 * np.pi / lam
    r1 = np.sqrt(X**2 + (Y - d/2)**2 + L**2)
    r2 = np.sqrt(X**2 + (Y + d/2)**2 + L**2)
    
    delta_phi = k * (r2 - r1)
    intensidad = np.cos(delta_phi / 2.0)**2
    return X, Y, intensidad

def calcular_patron_michelson(longitud_onda_nm, delta_d_um, f_lente_cm, tamano_pantalla_cm, resolucion=500):
    """Calcula las franjas de igual inclinación (anillos de Haidinger) de Michelson."""
    lam = float(longitud_onda_nm) * 1e-9
    delta_d = float(delta_d_um) * 1e-6  
    f = float(f_lente_cm) * 1e-2        
    tamano = float(tamano_pantalla_cm) * 1e-2
    
    x = np.linspace(-tamano/2, tamano/2, resolucion)
    y = np.linspace(-tamano/2, tamano/2, resolucion)
    X, Y = np.meshgrid(x, y)
    
    R = np.sqrt(X**2 + Y**2)
    theta = np.arctan(R / f)
    
    k = 2.0 * np.pi / lam
    delta_phi = k * (2.0 * delta_d * np.cos(theta))
    intensidad = np.cos(delta_phi / 2.0)**2
    return X, Y, intensidad

# ==========================================
# MÓDULO IV: DIFRACCIÓN DE FRAUNHOFER
# ==========================================

def calcular_difraccion_rendija(longitud_onda_nm, ancho_a_mm, L_cm, tamano_pantalla_cm, resolucion=500):
    """Calcula la difracción de Fraunhofer para una rendija simple vertical."""
    lam = float(longitud_onda_nm) * 1e-9
    a = float(ancho_a_mm) * 1e-3
    L = float(L_cm) * 1e-2
    tamano = float(tamano_pantalla_cm) * 1e-2
    
    x = np.linspace(-tamano/2, tamano/2, resolucion)
    y = np.linspace(-tamano/2, tamano/2, resolucion)
    X, Y = np.meshgrid(x, y)
    
    distancia = np.sqrt(X**2 + Y**2 + L**2)
    sin_theta_x = X / distancia
    
    factor_x = a * sin_theta_x / lam
    intensidad = np.sinc(factor_x)**2
    return X, Y, intensidad

def calcular_difraccion_rectangular(longitud_onda_nm, ancho_a_mm, altura_b_mm, L_cm, tamano_pantalla_cm, resolucion=500):
    """Calcula la distribución espacial exacta 2D para una apertura rectangular."""
    lam = float(longitud_onda_nm) * 1e-9
    a = float(ancho_a_mm) * 1e-3
    b = float(altura_b_mm) * 1e-3
    L = float(L_cm) * 1e-2
    tamano = float(tamano_pantalla_cm) * 1e-2
    
    x = np.linspace(-tamano/2, tamano/2, resolucion)
    y = np.linspace(-tamano/2, tamano/2, resolucion)
    X, Y = np.meshgrid(x, y)
    
    distancia = np.sqrt(X**2 + Y**2 + L**2)
    sin_theta_x = X / distancia
    sin_theta_y = Y / distancia
    
    factor_x = a * sin_theta_x / lam
    factor_y = b * sin_theta_y / lam
    
    intensidad = (np.sinc(factor_x)**2) * (np.sinc(factor_y)**2)
    return X, Y, intensidad

# ==========================================
# MÓDULO V: POLARIZACIÓN Y FORMALISMO DE JONES
# ==========================================

def vector_jones_inicial(estado):
    """Retorna el vector de Jones estructurado y normalizado."""
    if estado == 'Lineal Horizontal':
        return np.array([[1.0], [0.0]], dtype=complex)
    elif estado == 'Lineal Vertical':
        return np.array([[0.0], [1.0]], dtype=complex)
    elif estado == 'Lineal +45°':
        return np.array([[1.0/np.sqrt(2)], [1.0/np.sqrt(2)]], dtype=complex)
    elif estado == 'Circular Derecha':
        return np.array([[1.0/np.sqrt(2)], [-1j/np.sqrt(2)]], dtype=complex)
    elif estado == 'Circular Izquierda':
        return np.array([[1.0/np.sqrt(2)], [1j/np.sqrt(2)]], dtype=complex)
    else:
        return np.array([[1.0], [0.0]], dtype=complex)

def matriz_polarizador_lineal(theta_deg):
    """Matriz de Jones para un polarizador lineal orientado a theta grados."""
    th = np.radians(theta_deg)
    c, s = np.cos(th), np.sin(th)
    return np.array([[c**2, c*s], [c*s, s**2]], dtype=complex)

def matriz_retardador(theta_deg, gamma_deg):
    """Matriz de Jones para un retardador general con rotación espacial."""
    th = np.radians(theta_deg)
    gamma = np.radians(gamma_deg)
    c, s = np.cos(th), np.sin(th)
    
    R_inv = np.array([[c, -s], [s, c]], dtype=complex)
    R = np.array([[c, s], [-s, c]], dtype=complex)
    
    W = np.array([[np.exp(1j * gamma / 2.0), 0.0], 
                  [0.0, np.exp(-1j * gamma / 2.0)]], dtype=complex)
    
    return np.dot(R_inv, np.dot(W, R))

def curva_elipse_polarizacion(Ex, Ey, resolucion=300):
    """Genera la trayectoria temporal del vector de campo eléctrico real."""
    t = np.linspace(0, 2 * np.pi, resolucion)
    Ex_t = np.real(complex(Ex) * np.exp(-1j * t))
    Ey_t = np.real(complex(Ey) * np.exp(-1j * t))
    return Ex_t, Ey_t

def jones_a_euler_latex(Jx, Jy):
    """Traduce un estado de Jones complejo a expresiones nativas en formato LaTeX."""
    def formatear_componente(z):
        amp = np.abs(z)
        fase = np.angle(z) 
        
        if amp < 1e-4: 
            return "0"
        if abs(fase) < 1e-4: 
            return f"{amp:.2f}"
            
        return f"{amp:.2f} e^{{i {fase:.2f}}}"
    
    # Forzar conversión a escalares complejos nativos para blindar la operación
    comp_x = formatear_componente(complex(Jx))
    comp_y = formatear_componente(complex(Jy))
    
    return r"\vec{E}_{salida} = \begin{pmatrix} " + comp_x + r" \\ " + comp_y + r" \end{pmatrix}"