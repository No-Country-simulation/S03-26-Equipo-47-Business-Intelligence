"""
Utilidades para conexión y consultas a la base de datos
"""

import streamlit as st
import duckdb
import pandas as pd
from pathlib import Path

# ============================================
# CONFIGURACIÓN
# ============================================

DB_FILE = Path("database/technova.duckdb")

# ============================================
# FUNCIONES DE CONEXIÓN
# ============================================

@st.cache_resource
def get_connection():
    """
    Crea y retorna una conexión a DuckDB
    Usa cache_resource para mantener la conexión abierta
    """
    if not DB_FILE.exists():
        st.error(f"❌ Base de datos no encontrada: {DB_FILE}")
        st.info("💡 Por favor, ejecuta primero el script load.py para crear la base de datos")
        st.stop()
    
    return duckdb.connect(str(DB_FILE), read_only=True)

# ============================================
# FUNCIONES DE CARGA DE DIMENSIONES
# ============================================

@st.cache_data(ttl=300)
def load_dim_metrica():
    """Cargar catálogo completo de métricas"""
    conn = get_connection()
    return conn.execute("""
        SELECT * FROM dim_metrica
        ORDER BY id_metrica
    """).df()

@st.cache_data(ttl=300)
def load_dim_area():
    """Cargar todas las áreas"""
    conn = get_connection()
    return conn.execute("""
        SELECT * FROM dim_area
        ORDER BY nombre_area
    """).df()

@st.cache_data(ttl=300)
def load_dim_tiempo():
    """Cargar dimensión tiempo"""
    conn = get_connection()
    return conn.execute("""
        SELECT * FROM dim_tiempo
        ORDER BY fecha
    """).df()

@st.cache_data(ttl=300)
def load_dim_empleado():
    """Cargar información de empleados"""
    conn = get_connection()
    return conn.execute("""
        SELECT * FROM dim_empleado
        ORDER BY id_empleado
    """).df()

# ============================================
# FUNCIONES DE CARGA DE HECHOS
# ============================================

@st.cache_data(ttl=60)
def load_fact_monitoreo(fecha_inicio=None, fecha_fin=None, categoria=None, area=None):
    """
    Cargar tabla de hechos con filtros opcionales
    
    Args:
        fecha_inicio: Fecha de inicio (datetime o str)
        fecha_fin: Fecha de fin (datetime o str)
        categoria: Categoría ESG ('Financiera', 'E', 'S', 'G') o None
        area: Nombre del área o None
    
    Returns:
        DataFrame con los datos filtrados
    """
    conn = get_connection()
    
    query = """
        SELECT 
            f.id_monitoreo,
            f.id_tiempo,
            t.fecha,
            t.anio,
            t.mes,
            t.trimestre,
            t.nombre_mes,
            f.id_metrica,
            m.nombre as metrica,
            m.categoria,
            m.subcategoria,
            m.unidad,
            m.descripcion,
            f.id_area,
            a.nombre_area,
            f.valor,
            f.fuente
        FROM fact_monitoreo f
        JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo
        JOIN dim_metrica m ON f.id_metrica = m.id_metrica
        JOIN dim_area a ON f.id_area = a.id_area
        WHERE 1=1
    """
    
    params = []
    
    if fecha_inicio is not None:
        query += " AND t.fecha >= ?"
        params.append(pd.to_datetime(fecha_inicio))
    
    if fecha_fin is not None:
        query += " AND t.fecha <= ?"
        params.append(pd.to_datetime(fecha_fin))
    
    if categoria is not None and categoria != 'Todas':
        query += " AND m.categoria = ?"
        params.append(categoria)
    
    if area is not None and area != 'Todas':
        query += " AND a.nombre_area = ?"
        params.append(area)
    
    query += " ORDER BY t.fecha, f.id_metrica"
    
    df = conn.execute(query, params).df()
    
    # Convertir fecha a datetime si no lo es
    if not df.empty and 'fecha' in df.columns:
        df['fecha'] = pd.to_datetime(df['fecha'])
    
    return df

# ============================================
# CONSULTAS ESPECÍFICAS
# ============================================

@st.cache_data(ttl=60)
def get_metricas_by_categoria(categoria, fecha_inicio=None, fecha_fin=None):
    """
    Obtener todas las métricas de una categoría específica
    
    Args:
        categoria: 'Financiera', 'E', 'S', o 'G'
        fecha_inicio: Fecha inicio opcional
        fecha_fin: Fecha fin opcional
    
    Returns:
        DataFrame con las métricas de la categoría
    """
    return load_fact_monitoreo(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        categoria=categoria
    )

@st.cache_data(ttl=60)
def get_metrica_by_id(id_metrica, fecha_inicio=None, fecha_fin=None):
    """
    Obtener datos de una métrica específica
    
    Args:
        id_metrica: ID de la métrica
        fecha_inicio: Fecha inicio opcional
        fecha_fin: Fecha fin opcional
    
    Returns:
        DataFrame con los datos de la métrica
    """
    conn = get_connection()
    
    query = """
        SELECT 
            f.id_monitoreo,
            t.fecha,
            t.anio,
            t.mes,
            t.trimestre,
            m.nombre as metrica,
            m.categoria,
            m.unidad,
            a.nombre_area,
            f.valor,
            f.fuente
        FROM fact_monitoreo f
        JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo
        JOIN dim_metrica m ON f.id_metrica = m.id_metrica
        JOIN dim_area a ON f.id_area = a.id_area
        WHERE f.id_metrica = ?
    """
    
    params = [id_metrica]
    
    if fecha_inicio is not None:
        query += " AND t.fecha >= ?"
        params.append(pd.to_datetime(fecha_inicio))
    
    if fecha_fin is not None:
        query += " AND t.fecha <= ?"
        params.append(pd.to_datetime(fecha_fin))
    
    query += " ORDER BY t.fecha"
    
    df = conn.execute(query, params).df()
    
    if not df.empty and 'fecha' in df.columns:
        df['fecha'] = pd.to_datetime(df['fecha'])
    
    return df

@st.cache_data(ttl=60)
def get_latest_values():
    """
    Obtener los valores más recientes de todas las métricas
    
    Returns:
        DataFrame con los últimos valores
    """
    conn = get_connection()
    
    query = """
        WITH latest_date AS (
            SELECT MAX(t.fecha) as max_fecha
            FROM fact_monitoreo f
            JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo
        )
        SELECT 
            m.id_metrica,
            m.nombre as metrica,
            m.categoria,
            m.subcategoria,
            m.unidad,
            a.nombre_area,
            f.valor,
            t.fecha
        FROM fact_monitoreo f
        JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo
        JOIN dim_metrica m ON f.id_metrica = m.id_metrica
        JOIN dim_area a ON f.id_area = a.id_area
        WHERE t.fecha = (SELECT max_fecha FROM latest_date)
        ORDER BY m.id_metrica
    """
    
    return conn.execute(query).df()

@st.cache_data(ttl=60)
def get_date_range():
    """
    Obtener el rango de fechas disponible en la base de datos
    
    Returns:
        Tupla (fecha_min, fecha_max)
    """
    conn = get_connection()
    
    result = conn.execute("""
        SELECT 
            MIN(t.fecha) as min_fecha,
            MAX(t.fecha) as max_fecha
        FROM fact_monitoreo f
        JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo
    """).fetchone()
    
    return (pd.to_datetime(result[0]), pd.to_datetime(result[1]))

@st.cache_data(ttl=300)
def get_available_years():
    """
    Obtener lista de años disponibles
    
    Returns:
        Lista de años
    """
    conn = get_connection()
    
    result = conn.execute("""
        SELECT DISTINCT t.anio
        FROM fact_monitoreo f
        JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo
        ORDER BY t.anio
    """).df()
    
    return result['anio'].tolist()

# ============================================
# FUNCIONES DE AGREGACIÓN
# ============================================

@st.cache_data(ttl=60)
def get_monthly_aggregation(id_metrica, fecha_inicio=None, fecha_fin=None):
    """
    Obtener agregación mensual de una métrica
    
    Args:
        id_metrica: ID de la métrica
        fecha_inicio: Fecha inicio opcional
        fecha_fin: Fecha fin opcional
    
    Returns:
        DataFrame con valores mensuales agregados
    """
    conn = get_connection()
    
    query = """
        SELECT 
            t.anio,
            t.mes,
            t.nombre_mes,
            AVG(f.valor) as valor_promedio,
            SUM(f.valor) as valor_total,
            MIN(f.valor) as valor_minimo,
            MAX(f.valor) as valor_maximo,
            COUNT(*) as num_registros
        FROM fact_monitoreo f
        JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo
        WHERE f.id_metrica = ?
    """
    
    params = [id_metrica]
    
    if fecha_inicio is not None:
        query += " AND t.fecha >= ?"
        params.append(pd.to_datetime(fecha_inicio))
    
    if fecha_fin is not None:
        query += " AND t.fecha <= ?"
        params.append(pd.to_datetime(fecha_fin))
    
    query += " GROUP BY t.anio, t.mes, t.nombre_mes ORDER BY t.anio, t.mes"
    
    return conn.execute(query, params).df()

@st.cache_data(ttl=60)
def get_metrics_summary(fecha_inicio=None, fecha_fin=None):
    """
    Obtener resumen de todas las métricas
    
    Returns:
        DataFrame con estadísticas por métrica
    """
    conn = get_connection()
    
    query = """
        SELECT 
            m.id_metrica,
            m.nombre as metrica,
            m.categoria,
            m.unidad,
            COUNT(*) as num_registros,
            AVG(f.valor) as valor_promedio,
            MIN(f.valor) as valor_minimo,
            MAX(f.valor) as valor_maximo,
            STDDEV(f.valor) as desviacion_std
        FROM fact_monitoreo f
        JOIN dim_metrica m ON f.id_metrica = m.id_metrica
        JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo
        WHERE 1=1
    """
    
    params = []
    
    if fecha_inicio is not None:
        query += " AND t.fecha >= ?"
        params.append(pd.to_datetime(fecha_inicio))
    
    if fecha_fin is not None:
        query += " AND t.fecha <= ?"
        params.append(pd.to_datetime(fecha_fin))
    
    query += " GROUP BY m.id_metrica, m.nombre, m.categoria, m.unidad"
    query += " ORDER BY m.id_metrica"
    
    return conn.execute(query, params).df()