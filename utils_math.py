import numpy as np

def calcular_snell(n1, n2, theta_i_deg):
    """
    Calcula el ángulo de refracción utilizando la Ley de Snell.
    Retorna el ángulo refractado, un booleano indicando si hay Reflexión Total Interna (TIR),
    y el ángulo crítico (si existe).
    """
    # Convertimos a radianes para numpy
    theta_i_rad = np.radians(theta_i_deg)
    
    # Ley de Snell: n1 * sin(θi) = n2 * sin(θt)
    sin_theta_t = (n1 / n2) * np.sin(theta_i_rad)
    
    # Cálculo del ángulo crítico (solo si pasamos de un medio más denso a uno menos denso)
    theta_critico = np.degrees(np.arcsin(n2 / n1)) if n1 > n2 else None
    
    # Verificación de Reflexión Total Interna
    if sin_theta_t > 1.0:
        return None, True, theta_critico
        
    # Si hay refracción, calculamos el ángulo
    theta_t_rad = np.arcsin(sin_theta_t)
    theta_t_deg = np.degrees(theta_t_rad)
    
    return theta_t_deg, False, theta_critico

def calcular_fresnel(n1, n2, theta_i_deg, theta_t_deg, tir):
    """
    Calcula los coeficientes de reflectancia (R) y transmitancia (T)
    para las polarizaciones s y p utilizando las ecuaciones de Fresnel.
    """
    if tir:
        # En reflexión total interna, toda la energía se refleja
        return 1.0, 1.0, 0.0, 0.0

    # Conversión a radianes
    th_i = np.radians(theta_i_deg)
    th_t = np.radians(theta_t_deg)

    # Evitar divisiones entre cero en incidencia normal estricta (0 grados)
    if theta_i_deg == 0:
        R_normal = ((n1 - n2) / (n1 + n2))**2
        return R_normal, R_normal, 1.0 - R_normal, 1.0 - R_normal

    # Componentes trigonométricas comunes
    cos_i = np.cos(th_i)
    cos_t = np.cos(th_t)

    # Polarización Perpendicular (s)
    r_s = (n1 * cos_i - n2 * cos_t) / (n1 * cos_i + n2 * cos_t)
    R_s = r_s**2
    T_s = 1.0 - R_s

    # Polarización Paralela (p)
    r_p = (n1 * cos_t - n2 * cos_i) / (n1 * cos_t + n2 * cos_i)
    R_p = r_p**2
    T_p = 1.0 - R_p

    return R_s, R_p, T_s, T_p

 # ==========================================
# MÓDULO I: ÓPTICA GEOMÉTRICA (MATRICES ABCD)
# ==========================================

def matriz_translacion(d):
    """Matriz de propagación en el espacio libre por una distancia d."""
    return np.array([
        [1.0, float(d)],
        [0.0, 1.0]
    ])

def matriz_lente_delgada(f):
    """Matriz de transformación para una lente delgada de distancia focal f."""
    # Manejo de error para evitar división por cero si f = 0
    if f == 0:
        f = 1e-9
    return np.array([
        [1.0, 0.0],
        [-1.0 / float(f), 1.0]
    ])

def matriz_espejo_esferico(R):
    """Matriz de transformación para un espejo esférico de radio R."""
    if R == 0:
        R = 1e-9
    return np.array([
        [1.0, 0.0],
        [-2.0 / float(R), 1.0]
    ])

def trazar_rayo_sistema(y0, theta0_deg, componentes, d_final=20.0):
    """
    Traza un rayo a través de un sistema óptico.
    y0: Altura inicial
    theta0_deg: Ángulo inicial en grados
    componentes: Lista de tuplas (tipo, valor, distancia_previa)
    d_final: Distancia extra para trazar el rayo tras salir del sistema
    """
    # Vector de estado inicial [altura, ángulo en radianes]
    theta0_rad = np.radians(theta0_deg)
    rayo_actual = np.array([[y0], [theta0_rad]])
    
    # Listas para almacenar las coordenadas para la gráfica
    posiciones_z = [0.0]
    alturas_y = [y0]
    
    z_actual = 0.0
    
    for tipo, valor, d in componentes:
        # 1. Propagación por el espacio libre hasta el componente
        if d > 0:
            M_trans = matriz_translacion(d)
            rayo_actual = np.dot(M_trans, rayo_actual)
            z_actual += d
            posiciones_z.append(z_actual)
            alturas_y.append(rayo_actual[0, 0])
            
        # 2. Transformación por el componente óptico
        if tipo == 'lente':
            M_comp = matriz_lente_delgada(valor)
        elif tipo == 'espejo':
            M_comp = matriz_espejo_esferico(valor)
        else:
            continue
            
        rayo_actual = np.dot(M_comp, rayo_actual)
        
    # --- CORRECCIÓN: Propagación final después de la última lente ---
    if len(componentes) > 0:
        M_trans_final = matriz_translacion(d_final)
        rayo_actual = np.dot(M_trans_final, rayo_actual)
        z_actual += d_final
        posiciones_z.append(z_actual)
        alturas_y.append(rayo_actual[0, 0])
        
    return posiciones_z, alturas_y, rayo_actual

def obtener_matriz_sistema(componentes):
    """
    Calcula la matriz ABCD equivalente acumulada del sistema completo.
    Multiplica las matrices en orden cronológico (de derecha a izquierda algebraicamente).
    """
    # Iniciamos con la matriz identidad 2x2
    M_acumulada = np.eye(2)
    
    for tipo, valor, d in componentes:
        # 1. Aplicar traslación espacial previa si existe
        if d > 0:
            M_acumulada = np.dot(matriz_translacion(d), M_acumulada)
            
        # 2. Aplicar transformación del elemento óptico
        if tipo == 'lente':
            M_comp = matriz_lente_delgada(valor)
        elif tipo == 'espejo':
            M_comp = matriz_espejo_esferico(valor)
        else:
            continue
            
        M_acumulada = np.dot(M_comp, M_acumulada)
        
    return M_acumulada

# ==========================================
# MÓDULO III: INTERFERENCIA Y SUPERPOSICIÓN DE ONDAS
# ==========================================

def calcular_patron_young(longitud_onda_nm, d_mm, L_cm, tamano_pantalla_cm, resolucion=500):
    """
    Calcula el patrón de interferencia bidimensional exacto para la doble rendija.
    """
    # 1. Conversión estricta de unidades al Sistema Internacional (metros)
    lam = float(longitud_onda_nm) * 1e-9
    d = float(d_mm) * 1e-3
    L = float(L_cm) * 1e-2
    tamano = float(tamano_pantalla_cm) * 1e-2
    
    # 2. Creación de la malla bidimensional para la pantalla 
    # El eje Y es vertical (paralelo a la separación de las rendijas)
    # El eje X es horizontal (a lo largo de las rendijas)
    x = np.linspace(-tamano/2, tamano/2, resolucion)
    y = np.linspace(-tamano/2, tamano/2, resolucion)
    X, Y = np.meshgrid(x, y)
    
    # 3. Número de onda
    k = 2.0 * np.pi / lam
    
    # 4. Cálculo de distancias geométricas exactas (sin aproximación paraxial)
    # Rendija 1 en Y = d/2, Rendija 2 en Y = -d/2. Ambas en Z = 0.
    r1 = np.sqrt(X**2 + (Y - d/2)**2 + L**2)
    r2 = np.sqrt(X**2 + (Y + d/2)**2 + L**2)
    
    # 5. Superposición de fases e Intensidad
    delta_phi = k * (r2 - r1)
    
    # La intensidad se normaliza respecto a I_max
    intensidad = np.cos(delta_phi / 2.0)**2
    
    return X, Y, intensidad

def calcular_patron_michelson(longitud_onda_nm, delta_d_um, f_lente_cm, tamano_pantalla_cm, resolucion=500):
    """
    Calcula el patrón de interferencia de anillos concéntricos para un Interferómetro de Michelson.
    Asume franjas de igual inclinación (anillos de Haidinger) enfocadas por una lente.
    """
    # 1. Conversión de unidades al Sistema Internacional (metros)
    lam = float(longitud_onda_nm) * 1e-9
    delta_d = float(delta_d_um) * 1e-6  # Desfase del espejo en micrómetros
    f = float(f_lente_cm) * 1e-2        # Focal de la lente formadora de imagen
    tamano = float(tamano_pantalla_cm) * 1e-2
    
    # 2. Creación de la malla bidimensional
    x = np.linspace(-tamano/2, tamano/2, resolucion)
    y = np.linspace(-tamano/2, tamano/2, resolucion)
    X, Y = np.meshgrid(x, y)
    
    # 3. Cálculo del radio desde el centro óptico
    R = np.sqrt(X**2 + Y**2)
    
    # 4. Cálculo del ángulo de inclinación theta para cada punto (aprox. paraxial R/f)
    theta = np.arctan(R / f)
    
    # 5. Ecuación de diferencia de fase para anillos de Haidinger
    # delta_L = 2 * delta_d * cos(theta)
    k = 2.0 * np.pi / lam
    delta_phi = k * (2.0 * delta_d * np.cos(theta))
    
    # 6. Intensidad normalizada resultante
    intensidad = np.cos(delta_phi / 2.0)**2
    
    return X, Y, intensidad

# ==========================================
# MÓDULO IV: DIFRACCIÓN DE FRAUNHOFER
# ==========================================

def calcular_difraccion_rendija(longitud_onda_nm, ancho_a_mm, L_cm, tamano_pantalla_cm, resolucion=500):
    """
    Calcula el patrón de difracción de Fraunhofer para una rendija simple vertical.
    El patrón se extiende a lo largo del eje horizontal X.
    """
    lam = float(longitud_onda_nm) * 1e-9
    a = float(ancho_a_mm) * 1e-3
    L = float(L_cm) * 1e-2
    tamano = float(tamano_pantalla_cm) * 1e-2
    
    x = np.linspace(-tamano/2, tamano/2, resolucion)
    y = np.linspace(-tamano/2, tamano/2, resolucion)
    X, Y = np.meshgrid(x, y)
    
    # Proyección angular exacta para cada punto de la pantalla
    distancia = np.sqrt(X**2 + Y**2 + L**2)
    sin_theta_x = X / distancia
    
    # np.sinc en numpy calcula sin(pi*v)/(pi*v)
    factor_x = a * sin_theta_x / lam
    intensidad = np.sinc(factor_x)**2
    
    return X, Y, intensidad

def calcular_difraccion_rectangular(longitud_onda_nm, ancho_a_mm, altura_b_mm, L_cm, tamano_pantalla_cm, resolucion=500):
    """
    Calcula el patrón de difracción de Fraunhofer para una apertura rectangular (ancho 'a' y altura 'b').
    Genera una rejilla bidimensional de máximos secundarios.
    """
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
    
    # La irradiancia es el producto cruzado de ambos perfiles sinc^2
    intensidad = (np.sinc(factor_x)**2) * (np.sinc(factor_y)**2)
    
    return X, Y, intensidad

# ==========================================
# MÓDULO V: POLARIZACIÓN Y FORMALISMO DE JONES
# ==========================================

def vector_jones_inicial(estado):
    """Devuelve el vector de Jones normalizado para estados de polarización básicos."""
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
    """Matriz de Jones para un polarizador lineal con eje de transmisión a theta grados."""
    th = np.radians(theta_deg)
    c, s = np.cos(th), np.sin(th)
    return np.array([[c**2, c*s], [c*s, s**2]], dtype=complex)

def matriz_retardador(theta_deg, gamma_deg):
    """
    Matriz de Jones para una lámina retardadora.
    theta_deg: Ángulo del eje rápido.
    gamma_deg: Desfase introducido (ej. 90 para lambda/4, 180 para lambda/2).
    """
    th = np.radians(theta_deg)
    gamma = np.radians(gamma_deg)
    c, s = np.cos(th), np.sin(th)
    
    # Matrices de rotación
    R_inv = np.array([[c, -s], [s, c]], dtype=complex)
    R = np.array([[c, s], [-s, c]], dtype=complex)
    
    # Matriz del retardador con eje rápido alineado en X
    W = np.array([[np.exp(1j * gamma / 2.0), 0], 
                  [0, np.exp(-1j * gamma / 2.0)]], dtype=complex)
    
    return np.dot(R_inv, np.dot(W, R))

def curva_elipse_polarizacion(Ex, Ey, resolucion=300):
    """Genera las coordenadas paramétricas del campo eléctrico E(t) para graficar la elipse."""
    t = np.linspace(0, 2 * np.pi, resolucion)
    # Extraemos la parte real de E * e^(-iwt)
    Ex_t = np.real(Ex * np.exp(-1j * t))
    Ey_t = np.real(Ey * np.exp(-1j * t))
    return Ex_t, Ey_t

def analizar_camino_optico(n1, n2, x_A, y_A, x_B, y_B, x_interfaz, resolucion=200):
    """
    Calcula el Camino Óptico (OPL) para un punto arbitrario x_interfaz.
    También genera un arreglo de valores para trazar la curva de minimización.
    """
    # Cálculo puntual para el slider del estudiante
    L1_puntual = np.sqrt((x_interfaz - x_A)**2 + y_A**2)
    L2_puntual = np.sqrt((x_B - x_interfaz)**2 + y_B**2)
    opl_puntual = n1 * L1_puntual + n2 * L2_puntual
    
    # Arreglo para la curva analítica (barrido de X entre x_A y x_B extendido)
    x_array = np.linspace(x_A - 2, x_B + 2, resolucion)
    L1_array = np.sqrt((x_array - x_A)**2 + y_A**2)
    L2_array = np.sqrt((x_B - x_array)**2 + y_B**2)
    opl_array = n1 * L1_array + n2 * L2_array
    
    # Encontrar el mínimo numérico exacto (el rayo real)
    indice_min = np.argmin(opl_array)
    x_min = x_array[indice_min]
    opl_min = opl_array[indice_min]
    
    return opl_puntual, x_array, opl_array, x_min, opl_min