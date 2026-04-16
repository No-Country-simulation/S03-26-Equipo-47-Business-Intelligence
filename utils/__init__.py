"""
Módulo de utilidades para Sustainable Growth Monitor
"""

from .database import *
from .config import *
from .analytics import *
from .components import *

__all__ = [
    # Database
    'get_connection',
    'load_dim_metrica',
    'load_dim_area',
    'load_dim_tiempo',
    'load_fact_monitoreo',
    'get_latest_values',
    'get_date_range',
    
    # Config
    'UMBRALES',
    'COLORES_CATEGORIA',
    'COLORES_ESTADO',
    'calcular_estado_metrica',
    'formatear_valor',
    'obtener_recomendacion',
    
    # Analytics
    'calcular_tendencia',
    'calcular_variacion',
    'calcular_correlacion',
    'interpretar_correlacion',
    
    # Components
    'render_filtros_sidebar',
    'render_kpi_card',
    'render_grafico_tendencia',
    'render_alerta',
]