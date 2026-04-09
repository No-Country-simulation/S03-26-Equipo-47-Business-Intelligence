"""
Funciones de análisis y cálculo de métricas
"""

import pandas as pd
import numpy as np
from scipy import stats

# ============================================
# ANÁLISIS DE TENDENCIAS
# ============================================

def calcular_tendencia(serie_valores):
    """
    Calcula la tendencia de una serie temporal usando regresión lineal
    
    Args:
        serie_valores: Series o array de valores
    
    Returns:
        float: Pendiente de la regresión (positiva = creciente, negativa = decreciente)
    """
    if len(serie_valores) < 2:
        return 0
    
    # Limpiar valores nulos
    serie_limpia = pd.Series(serie_valores).dropna()
    
    if len(serie_limpia) < 2:
        return 0
    
    x = np.arange(len(serie_limpia))
    y = serie_limpia.values
    
    # Regresión lineal simple
    try:
        slope, _, _, _, _ = stats.linregress(x, y)
        return slope
    except:
        return 0

def calcular_variacion(valor_actual, valor_anterior):
    """
    Calcula la variación porcentual entre dos valores
    
    Args:
        valor_actual: Valor del período actual
        valor_anterior: Valor del período anterior
    
    Returns:
        tuple: (variacion_absoluta, variacion_porcentual)
    """
    if valor_anterior == 0 or pd.isna(valor_anterior):
        return (0, 0)
    
    variacion_abs = valor_actual - valor_anterior
    variacion_pct = (variacion_abs / valor_anterior) * 100
    
    return (variacion_abs, variacion_pct)

# ============================================
# AGREGACIONES TEMPORALES
# ============================================

def agregar_por_mes(df, col_valor='valor'):
    """
    Agrupa datos por año y mes
    
    Args:
        df: DataFrame con columnas 'anio', 'mes' y col_valor
        col_valor: Nombre de la columna con valores a agregar
    
    Returns:
        DataFrame agregado por mes
    """
    if df.empty:
        return pd.DataFrame()
    
    resultado = df.groupby(['anio', 'mes']).agg({
        col_valor: ['sum', 'mean', 'min', 'max', 'count']
    }).reset_index()
    
    # Aplanar columnas multinivel
    resultado.columns = ['anio', 'mes', 'valor_total', 'valor_promedio', 
                         'valor_minimo', 'valor_maximo', 'num_registros']
    
    # Crear columna de fecha
    resultado['fecha'] = pd.to_datetime(resultado[['anio', 'mes']].assign(day=1))
    
    return resultado

def agregar_por_trimestre(df, col_valor='valor'):
    """
    Agrupa datos por año y trimestre
    
    Args:
        df: DataFrame con columnas 'anio', 'trimestre' y col_valor
        col_valor: Nombre de la columna con valores a agregar
    
    Returns:
        DataFrame agregado por trimestre
    """
    if df.empty:
        return pd.DataFrame()
    
    resultado = df.groupby(['anio', 'trimestre']).agg({
        col_valor: ['sum', 'mean', 'min', 'max', 'count']
    }).reset_index()
    
    resultado.columns = ['anio', 'trimestre', 'valor_total', 'valor_promedio',
                         'valor_minimo', 'valor_maximo', 'num_registros']
    
    return resultado

# ============================================
# ANÁLISIS DE CORRELACIONES
# ============================================

def calcular_correlacion(df1, df2, metodo='pearson'):
    """
    Calcula la correlación entre dos series de datos
    
    Args:
        df1: DataFrame con primera métrica
        df2: DataFrame con segunda métrica
        metodo: 'pearson', 'spearman', o 'kendall'
    
    Returns:
        tuple: (coeficiente_correlacion, p_valor)
    """
    # Asegurar que ambos DataFrames tienen la misma estructura temporal
    merged = pd.merge(
        df1[['anio', 'mes', 'valor']].rename(columns={'valor': 'valor1'}),
        df2[['anio', 'mes', 'valor']].rename(columns={'valor': 'valor2'}),
        on=['anio', 'mes'],
        how='inner'
    )
    
    if len(merged) < 3:  # Necesitamos al menos 3 puntos
        return (None, None)
    
    try:
        if metodo == 'pearson':
            corr, p_valor = stats.pearsonr(merged['valor1'], merged['valor2'])
        elif metodo == 'spearman':
            corr, p_valor = stats.spearmanr(merged['valor1'], merged['valor2'])
        else:
            corr, p_valor = stats.kendalltau(merged['valor1'], merged['valor2'])
        
        return (corr, p_valor)
    except:
        return (None, None)

def interpretar_correlacion(coef_correlacion):
    """
    Interpreta el coeficiente de correlación
    
    Args:
        coef_correlacion: Valor entre -1 y 1
    
    Returns:
        tuple: (categoria, descripcion, emoji)
    """
    if coef_correlacion is None or pd.isna(coef_correlacion):
        return ('Sin datos', 'No hay suficientes datos para calcular', '⚪')
    
    abs_corr = abs(coef_correlacion)
    
    if abs_corr >= 0.7:
        fuerza = 'Fuerte'
        emoji = '💪'
    elif abs_corr >= 0.4:
        fuerza = 'Moderada'
        emoji = '👍'
    else:
        fuerza = 'Débil'
        emoji = '🤏'
    
    direccion = 'positiva' if coef_correlacion > 0 else 'negativa'
    
    descripcion = f"Correlación {direccion} {fuerza.lower()}"
    categoria = f"{direccion.capitalize()} {fuerza}"
    
    return (categoria, descripcion, emoji)

# ============================================
# ANÁLISIS COMPARATIVO
# ============================================

def comparar_periodos(df_actual, df_anterior):
    """
    Compara métricas entre dos períodos
    
    Args:
        df_actual: DataFrame del período actual
        df_anterior: DataFrame del período anterior
    
    Returns:
        DataFrame con comparación
    """
    if df_actual.empty or df_anterior.empty:
        return pd.DataFrame()
    
    comparacion = []
    
    for metrica in df_actual['metrica'].unique():
        valor_actual = df_actual[df_actual['metrica'] == metrica]['valor'].sum()
        valor_anterior = df_anterior[df_anterior['metrica'] == metrica]['valor'].sum()
        
        var_abs, var_pct = calcular_variacion(valor_actual, valor_anterior)
        
        comparacion.append({
            'metrica': metrica,
            'valor_actual': valor_actual,
            'valor_anterior': valor_anterior,
            'variacion_absoluta': var_abs,
            'variacion_porcentual': var_pct
        })
    
    return pd.DataFrame(comparacion)

# ============================================
# ESTADÍSTICAS DESCRIPTIVAS
# ============================================

def calcular_estadisticas(serie):
    """
    Calcula estadísticas descriptivas de una serie
    
    Args:
        serie: Series o array de valores
    
    Returns:
        dict con estadísticas
    """
    serie_limpia = pd.Series(serie).dropna()
    
    if len(serie_limpia) == 0:
        return {
            'count': 0,
            'mean': None,
            'median': None,
            'std': None,
            'min': None,
            'max': None,
            'q25': None,
            'q75': None
        }
    
    return {
        'count': len(serie_limpia),
        'mean': serie_limpia.mean(),
        'median': serie_limpia.median(),
        'std': serie_limpia.std(),
        'min': serie_limpia.min(),
        'max': serie_limpia.max(),
        'q25': serie_limpia.quantile(0.25),
        'q75': serie_limpia.quantile(0.75)
    }

# ============================================
# DETECCIÓN DE ANOMALÍAS
# ============================================

def detectar_anomalias(serie, umbral_desviaciones=2):
    """
    Detecta valores anómalos usando desviación estándar
    
    Args:
        serie: Series o array de valores
        umbral_desviaciones: Número de desviaciones estándar para considerar anomalía
    
    Returns:
        array booleano indicando si cada valor es anómalo
    """
    serie_limpia = pd.Series(serie).dropna()
    
    if len(serie_limpia) < 3:
        return np.array([False] * len(serie))
    
    media = serie_limpia.mean()
    std = serie_limpia.std()
    
    # Si no hay variación, no hay anomalías
    if std == 0:
        return np.array([False] * len(serie))
    
    # Calcular z-score
    z_scores = np.abs((serie - media) / std)
    
    return z_scores > umbral_desviaciones

# ============================================
# PROYECCIONES SIMPLES
# ============================================

def proyectar_tendencia(serie, periodos_futuros=3):
    """
    Proyecta valores futuros basándose en tendencia lineal
    
    Args:
        serie: Series de valores históricos
        periodos_futuros: Número de períodos a proyectar
    
    Returns:
        array con valores proyectados
    """
    serie_limpia = pd.Series(serie).dropna()
    
    if len(serie_limpia) < 2:
        return np.array([serie_limpia.iloc[-1]] * periodos_futuros if len(serie_limpia) > 0 else [])
    
    x = np.arange(len(serie_limpia))
    y = serie_limpia.values
    
    try:
        slope, intercept, _, _, _ = stats.linregress(x, y)
        
        # Proyectar
        x_futuro = np.arange(len(serie_limpia), len(serie_limpia) + periodos_futuros)
        proyeccion = slope * x_futuro + intercept
        
        return proyeccion
    except:
        # Si falla, retornar último valor conocido
        return np.array([serie_limpia.iloc[-1]] * periodos_futuros)

# ============================================
# CÁLCULO DE MÉTRICAS DERIVADAS
# ============================================

def calcular_intensidad_energetica(df_energia, df_ingresos):
    """
    Calcula la intensidad energética (kWh por peso de ingreso)
    
    Args:
        df_energia: DataFrame con consumo energético
        df_ingresos: DataFrame con ingresos
    
    Returns:
        DataFrame con intensidad energética
    """
    merged = pd.merge(
        df_energia.groupby(['anio', 'mes'])['valor'].sum().reset_index().rename(columns={'valor': 'energia'}),
        df_ingresos.groupby(['anio', 'mes'])['valor'].sum().reset_index().rename(columns={'valor': 'ingresos'}),
        on=['anio', 'mes'],
        how='inner'
    )
    
    merged['intensidad_energetica'] = merged['energia'] / merged['ingresos']
    merged['fecha'] = pd.to_datetime(merged[['anio', 'mes']].assign(day=1))
    
    return merged

def calcular_productividad_empleado(df_ingresos, num_empleados):
    """
    Calcula productividad por empleado
    
    Args:
        df_ingresos: DataFrame con ingresos
        num_empleados: Número de empleados
    
    Returns:
        DataFrame con productividad
    """
    productividad = df_ingresos.copy()
    productividad['productividad'] = productividad['valor'] / num_empleados
    
    return productividad

def calcular_margen_operativo(df_ingresos, df_costos, df_gastos):
    """
    Calcula el margen operativo
    
    Args:
        df_ingresos: DataFrame con ingresos
        df_costos: DataFrame con costos
        df_gastos: DataFrame con gastos
    
    Returns:
        DataFrame con margen operativo
    """
    # Agrupar por mes
    ingresos = df_ingresos.groupby(['anio', 'mes'])['valor'].sum().reset_index().rename(columns={'valor': 'ingresos'})
    costos = df_costos.groupby(['anio', 'mes'])['valor'].sum().reset_index().rename(columns={'valor': 'costos'})
    gastos = df_gastos.groupby(['anio', 'mes'])['valor'].sum().reset_index().rename(columns={'valor': 'gastos'})
    
    # Merge
    merged = ingresos.merge(costos, on=['anio', 'mes'], how='inner')
    merged = merged.merge(gastos, on=['anio', 'mes'], how='inner')
    
    # Calcular margen
    merged['margen_operativo'] = ((merged['ingresos'] - merged['costos'] - merged['gastos']) / merged['ingresos']) * 100
    merged['fecha'] = pd.to_datetime(merged[['anio', 'mes']].assign(day=1))
    
    return merged