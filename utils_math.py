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