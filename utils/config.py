"""
Configuración de umbrales, constantes y utilidades compartidas
"""

# ============================================
# UMBRALES DE MÉTRICAS
# ============================================

# Formato: id_metrica: {'critico': valor, 'precaucion': valor, 'optimo': valor}
# Para métricas donde MAYOR es MEJOR: critico < precaucion < optimo
# Para métricas donde MENOR es MEJOR: optimo < precaucion < critico

UMBRALES = {
    1: {
        'nombre': 'Ingresos',
        'critico': 0,
        'precaucion': 1000000,
        'optimo': 5000000,
        'tipo': 'mayor_mejor'  # Mayor valor es mejor
    },
    2: {
        'nombre': 'Costo Compras',
        'critico': 1000000,
        'precaucion': 500000,
        'optimo': 200000,
        'tipo': 'menor_mejor'  # Menor valor es mejor
    },
    3: {
        'nombre': 'Gasto Personal',
        'critico': 800000,
        'precaucion': 500000,
        'optimo': 300000,
        'tipo': 'menor_mejor'
    },
    4: {
        'nombre': 'Consumo Energético',
        'critico': 150000,
        'precaucion': 120000,
        'optimo': 80000,
        'tipo': 'menor_mejor'
    },
    5: {
        'nombre': 'Tasa Reciclaje',
        'critico': 30,
        'precaucion': 60,
        'optimo': 80,
        'tipo': 'mayor_mejor'
    },
    6: {
        'nombre': 'Satisfacción Laboral',
        'critico': 6.0,
        'precaucion': 7.5,
        'optimo': 8.5,
        'tipo': 'mayor_mejor'
    },
    7: {
        'nombre': 'Horas Capacitación',
        'critico': 10,
        'precaucion': 20,
        'optimo': 40,
        'tipo': 'mayor_mejor'
    },
    8: {
        'nombre': 'Días Baja Accidentes',
        'critico': 15,
        'precaucion': 8,
        'optimo': 3,
        'tipo': 'menor_mejor'
    }
}

# ============================================
# COLORES POR CATEGORÍA ESG
# ============================================

COLORES_CATEGORIA = {
    'Financiera': '#1f77b4',  # Azul
    'E': '#2ca02c',           # Verde (Environmental)
    'S': '#ff7f0e',           # Naranja (Social)
    'G': '#9467bd'            # Púrpura (Governance)
}

COLORES_ESTADO = {
    'critical': '#d62728',    # Rojo
    'warning': '#ff7f0e',     # Naranja
    'optimal': '#2ca02c',     # Verde
    'neutral': '#7f7f7f'      # Gris
}

# ============================================
# CONFIGURACIÓN DE VISUALIZACIÓN
# ============================================

ALTURA_GRAFICOS = {
    'kpi': 250,
    'tendencia': 350,
    'correlacion': 300,
    'comparativa': 300,
    'detalle': 400
}

# ============================================
# MAPEO DE IDS A CATEGORÍAS
# ============================================

METRICAS_POR_CATEGORIA = {
    'Financiera': [1, 2, 3],      # Ingresos, Costos, Gastos
    'E': [4, 5],                   # Energía, Reciclaje
    'S': [6, 7, 8],               # Satisfacción, Capacitación, Accidentes
    'G': []                        # Governance (no implementado aún)
}

# ============================================
# DESCRIPCIONES DE MÉTRICAS
# ============================================

DESCRIPCIONES_METRICAS = {
    1: {
        'titulo': '💰 Ingresos Totales',
        'descripcion': 'Suma de todas las ventas del período. Indica la capacidad de generación de ingresos del negocio.',
        'objetivo': 'Maximizar y mantener tendencia creciente',
        'acciones_mejora': [
            'Diversificar canales de venta',
            'Mejorar retención de clientes',
            'Aumentar ticket promedio',
            'Expandir líneas de producto'
        ]
    },
    2: {
        'titulo': '💸 Costo de Compras',
        'descripcion': 'Total de compras a proveedores. Refleja eficiencia en adquisición de insumos.',
        'objetivo': 'Minimizar sin comprometer calidad',
        'acciones_mejora': [
            'Negociar mejores precios con proveedores',
            'Optimizar inventarios',
            'Consolidar compras',
            'Evaluar proveedores alternativos'
        ]
    },
    3: {
        'titulo': '👥 Gasto de Personal',
        'descripcion': 'Suma de salarios, bonos y cargas sociales. Principal componente de costos operativos.',
        'objetivo': 'Optimizar productividad por empleado',
        'acciones_mejora': [
            'Mejorar procesos y automatización',
            'Capacitación en eficiencia',
            'Revisar estructura organizacional',
            'Implementar bonos por desempeño'
        ]
    },
    4: {
        'titulo': '⚡ Consumo Energético',
        'descripcion': 'Consumo total de energía eléctrica y combustibles. Impacto directo en costos y huella de carbono.',
        'objetivo': 'Reducir 8% anual',
        'acciones_mejora': [
            'Auditoría energética completa',
            'Inversión en equipos eficientes',
            'Implementar paneles solares',
            'Optimizar horarios de operación'
        ]
    },
    5: {
        'titulo': '♻️ Tasa de Reciclaje',
        'descripcion': 'Porcentaje de residuos reciclados vs total generado. Indicador clave de sostenibilidad.',
        'objetivo': 'Alcanzar >60%, ideal >80%',
        'acciones_mejora': [
            'Programa de separación en origen',
            'Capacitación en reciclaje',
            'Mejorar señalización',
            'Alianzas con recicladores'
        ]
    },
    6: {
        'titulo': '😊 Satisfacción Laboral',
        'descripcion': 'Promedio de encuestas de satisfacción (1-10). Refleja clima organizacional.',
        'objetivo': 'Mantener >7.5 puntos',
        'acciones_mejora': [
            'Focus groups y escucha activa',
            'Mejorar beneficios y condiciones',
            'Programas de reconocimiento',
            'Balance vida-trabajo'
        ]
    },
    7: {
        'titulo': '📚 Horas de Capacitación',
        'descripcion': 'Total de horas de formación por empleado. Inversión en desarrollo profesional.',
        'objetivo': '>20 horas/empleado/año',
        'acciones_mejora': [
            'Plan anual de capacitación',
            'Cursos online accesibles',
            'Mentoría interna',
            'Certificaciones profesionales'
        ]
    },
    8: {
        'titulo': '🏥 Días de Baja por Accidentes',
        'descripcion': 'Días de ausencia por accidentes laborales. Indicador de seguridad e higiene.',
        'objetivo': 'Tender a 0 accidentes',
        'acciones_mejora': [
            'Programa de seguridad e higiene',
            'Capacitación en prevención',
            'Revisión de EPP',
            'Auditorías de seguridad'
        ]
    }
}

# ============================================
# RECOMENDACIONES POR ESTADO
# ============================================

RECOMENDACIONES = {
    4: {  # Consumo Energético
        'critical': '🔴 **URGENTE**: Realizar auditoría energética inmediata. Revisar equipos de alto consumo y considerar inversión en renovables.',
        'warning': '🟡 **ATENCIÓN**: Implementar medidas de eficiencia energética. Revisar horarios de operación y equipamiento.'
    },
    5: {  # Tasa Reciclaje
        'critical': '🔴 **URGENTE**: Implementar programa integral de separación de residuos. Capacitar al personal en reciclaje.',
        'warning': '🟡 **ATENCIÓN**: Mejorar señalización de puntos de reciclaje. Auditar proveedores de gestión de residuos.'
    },
    6: {  # Satisfacción Laboral
        'critical': '🔴 **URGENTE**: Realizar focus groups inmediatos. Revisar políticas de RRHH y condiciones laborales.',
        'warning': '🟡 **ATENCIÓN**: Encuestas de seguimiento. Implementar programa de reconocimiento y desarrollo.'
    },
    1: {  # Ingresos
        'warning': '🟡 **ATENCIÓN**: Revisar estrategia comercial. Diversificar canales de venta y analizar competencia.'
    },
    8: {  # Accidentes
        'critical': '🔴 **URGENTE**: Revisar protocolos de seguridad. Auditoría inmediata de condiciones laborales.',
        'warning': '🟡 **ATENCIÓN**: Reforzar capacitación en prevención. Revisar equipos de protección personal.'
    }
}

# ============================================
# FUNCIONES DE UTILIDAD
# ============================================

def calcular_estado_metrica(id_metrica, valor):
    """
    Determina el estado de una métrica según umbrales
    
    Args:
        id_metrica: ID de la métrica
        valor: Valor actual de la métrica
    
    Returns:
        Tupla (emoji, estado_string)
        - emoji: '🔴', '🟡', '🟢', o '⚪'
        - estado: 'critical', 'warning', 'optimal', o 'neutral'
    """
    if id_metrica not in UMBRALES:
        return '⚪', 'neutral'
    
    umbral = UMBRALES[id_metrica]
    tipo = umbral.get('tipo', 'mayor_mejor')
    
    if tipo == 'menor_mejor':
        # Para métricas donde MENOR es MEJOR (costos, consumo, accidentes)
        if valor <= umbral['optimo']:
            return '🟢', 'optimal'
        elif valor <= umbral['precaucion']:
            return '🟡', 'warning'
        else:
            return '🔴', 'critical'
    else:
        # Para métricas donde MAYOR es MEJOR (ingresos, reciclaje, satisfacción)
        if valor >= umbral['optimo']:
            return '🟢', 'optimal'
        elif valor >= umbral['precaucion']:
            return '🟡', 'warning'
        else:
            return '🔴', 'critical'

def obtener_recomendacion(id_metrica, estado):
    """
    Obtiene la recomendación para una métrica en un estado específico
    
    Args:
        id_metrica: ID de la métrica
        estado: 'critical', 'warning', u 'optimal'
    
    Returns:
        String con la recomendación o None
    """
    if id_metrica not in RECOMENDACIONES:
        return None
    
    return RECOMENDACIONES[id_metrica].get(estado)

def formatear_valor(valor, unidad):
    """
    Formatea un valor según su unidad
    
    Args:
        valor: Valor numérico
        unidad: Unidad de medida
    
    Returns:
        String formateado
    """
    if unidad == 'ARS':
        return f"${valor:,.0f}"
    elif unidad == '%':
        return f"{valor:.1f}%"
    elif unidad == 'kWh':
        return f"{valor:,.0f} kWh"
    elif unidad == 'puntos':
        return f"{valor:.1f} pts"
    elif unidad == 'horas':
        return f"{valor:,.0f} hs"
    elif unidad == 'días':
        return f"{valor:,.0f} días"
    else:
        return f"{valor:,.1f} {unidad}"

def obtener_color_categoria(categoria):
    """Retorna el color asociado a una categoría"""
    return COLORES_CATEGORIA.get(categoria, '#7f7f7f')

def obtener_color_estado(estado):
    """Retorna el color asociado a un estado"""
    return COLORES_ESTADO.get(estado, '#7f7f7f')