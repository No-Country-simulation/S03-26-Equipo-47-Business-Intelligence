"""
🎯 Core Module - Arquitectura Base con Patrones de Diseño
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import streamlit as st

# ============================================
# DATA CLASSES
# ============================================

@dataclass
class MetricConfig:
    """Configuración de una métrica"""
    id: int
    nombre: str
    categoria: str
    unidad: str
    color: str
    descripcion: str
    objetivo_tipo: str = "mayor_mejor"

@dataclass
class FilterConfig:
    """Configuración de filtros"""
    fecha_inicio: datetime
    fecha_fin: datetime
    categoria: Optional[str] = None
    area: Optional[str] = None

@dataclass
class ChartConfig:
    """Configuración de un gráfico"""
    titulo: str
    tipo: str
    altura: int = 350
    color: Optional[str] = None
    mostrar_objetivo: bool = False
    valor_objetivo: Optional[float] = None

# ============================================
# REPOSITORY PATTERN
# ============================================

class DataRepository(ABC):
    """Abstracción para acceso a datos"""
    
    @abstractmethod
    def get_fact_monitoreo(self, filtros: FilterConfig) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_date_range(self) -> Tuple[datetime, datetime]:
        pass
    
    @abstractmethod
    def get_metricas(self) -> List[MetricConfig]:
        pass
    
    @abstractmethod
    def get_areas(self) -> List[str]:
        pass

# ============================================
# STRATEGY PATTERN - Chart Strategies
# ============================================

class ChartStrategy(ABC):
    """Estrategia abstracta para gráficos"""
    
    @abstractmethod
    def crear_grafico(self, df: pd.DataFrame, config: ChartConfig) -> Any:
        pass

class LineChartStrategy(ChartStrategy):
    def crear_grafico(self, df: pd.DataFrame, config: ChartConfig) -> Any:
        import plotly.express as px
        import plotly.graph_objects as go
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['fecha'],
            y=df['valor'],
            mode='lines+markers',
            name='Valor',
            line=dict(color=config.color or '#1f77b4', width=2),
            marker=dict(size=6)
        ))
        
        if config.mostrar_objetivo and config.valor_objetivo:
            fig.add_hline(
                y=config.valor_objetivo,
                line_dash="dash",
                line_color="green",
                annotation_text=f"Objetivo"
            )
        
        fig.update_layout(
            title=config.titulo,
            height=config.altura,
            xaxis_title='',
            yaxis_title='Valor',
            hovermode='x unified'
        )
        
        return fig

class BarChartStrategy(ChartStrategy):
    def crear_grafico(self, df: pd.DataFrame, config: ChartConfig) -> Any:
        import plotly.express as px
        
        fig = px.bar(
            df,
            x='fecha',
            y='valor',
            title=config.titulo,
            color_discrete_sequence=[config.color or '#1f77b4']
        )
        
        fig.update_layout(
            height=config.altura,
            xaxis_title='',
            yaxis_title='Valor',
            hovermode='x unified'
        )
        
        return fig

class AreaChartStrategy(ChartStrategy):
    def crear_grafico(self, df: pd.DataFrame, config: ChartConfig) -> Any:
        import plotly.graph_objects as go
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['fecha'],
            y=df['valor'],
            mode='lines',
            fill='tozeroy',
            name='Valor',
            line=dict(color=config.color or '#2ca02c', width=2)
        ))
        
        fig.update_layout(
            title=config.titulo,
            height=config.altura,
            xaxis_title='',
            yaxis_title='Valor',
            hovermode='x unified'
        )
        
        return fig

class ChartStrategyFactory:
    """Factory para estrategias de gráficos"""
    
    _strategies = {
        'linea': LineChartStrategy,
        'barras': BarChartStrategy,
        'area': AreaChartStrategy
    }
    
    @classmethod
    def get_strategy(cls, tipo: str) -> ChartStrategy:
        strategy_class = cls._strategies.get(tipo.lower())
        if not strategy_class:
            raise ValueError(f"Tipo de gráfico no soportado: {tipo}")
        return strategy_class()

# ============================================
# SERVICE LAYER
# ============================================

class MetricService:
    """Servicio para lógica de negocio de métricas"""
    
    def __init__(self, repository: DataRepository):
        self.repo = repository
    
    def get_valores_actuales(self, filtros: FilterConfig) -> Dict[int, float]:
        """Obtiene valores actuales de todas las métricas"""
        df = self.repo.get_fact_monitoreo(filtros)
        
        if df.empty:
            return {}
        
        fecha_max = df['fecha'].max()
        df_ultimo = df[df['fecha'] == fecha_max]
        
        return dict(zip(df_ultimo['id_metrica'], df_ultimo['valor']))
    
    def get_evolucion_mensual(self, id_metrica: int, filtros: FilterConfig) -> pd.DataFrame:
        """Obtiene evolución mensual de una métrica"""
        df = self.repo.get_fact_monitoreo(filtros)
        df_metrica = df[df['id_metrica'] == id_metrica].copy()
        
        if df_metrica.empty:
            return pd.DataFrame()
        
        df_monthly = df_metrica.groupby(['anio', 'mes']).agg({
            'valor': 'sum'
        }).reset_index()
        
        df_monthly['fecha'] = pd.to_datetime(
            df_monthly.rename(columns={'anio': 'year', 'mes': 'month'})[['year', 'month']].assign(day=1)
        )
        
        return df_monthly[['fecha', 'valor']].sort_values('fecha')
    
    def calcular_estadisticas(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calcula estadísticas descriptivas"""
        if df.empty:
            return {
                'total': 0,
                'promedio': 0,
                'maximo': 0,
                'minimo': 0,
                'variacion': 0
            }
        
        stats = {
            'total': df['valor'].sum(),
            'promedio': df['valor'].mean(),
            'maximo': df['valor'].max(),
            'minimo': df['valor'].min()
        }
        
        if len(df) >= 2:
            primer_valor = df.iloc[0]['valor']
            ultimo_valor = df.iloc[-1]['valor']
            if primer_valor != 0:
                stats['variacion'] = ((ultimo_valor - primer_valor) / primer_valor) * 100
            else:
                stats['variacion'] = 0
        else:
            stats['variacion'] = 0
        
        return stats

# ============================================
# COMPONENT FACTORY
# ============================================

class ComponentFactory:
    """Factory para componentes UI reutilizables"""
    
    @staticmethod
    def crear_kpi_card(titulo: str, valor: float, unidad: str, 
                       variacion: Optional[float] = None,
                       border: bool = True):
        """Crea una tarjeta KPI"""
        from utils.formatters import formatear_valor
        
        valor_formateado = formatear_valor(valor, unidad)
        
        if variacion is not None:
            delta = f"{variacion:+.1f}%"
            st.metric(titulo, valor_formateado, delta, border=border)
        else:
            st.metric(titulo, valor_formateado, border=border)
    
    @staticmethod
    def crear_seccion_stats(stats: Dict[str, float], unidad: str):
        """Crea sección con 4 métricas de resumen"""
        from utils.formatters import formatear_valor
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total", formatear_valor(stats['total'], unidad), border=True)
        
        with col2:
            st.metric("Promedio", formatear_valor(stats['promedio'], unidad), border=True)
        
        with col3:
            st.metric("Máximo", formatear_valor(stats['maximo'], unidad), border=True)
        
        with col4:
            variacion = stats.get('variacion', 0)
            st.metric("Variación", f"{variacion:+.1f}%", border=True)

# ============================================
# BASE PAGE CLASS (Template Method Pattern)
# ============================================

class BasePage(ABC):
    """Clase base para todas las páginas"""
    
    def __init__(self, repository: DataRepository, metric_service: MetricService):
        self.repo = repository
        self.metric_service = metric_service
        self.configurar_pagina()
    
    @abstractmethod
    def configurar_pagina(self):
        """Configura parámetros de la página"""
        pass
    
    @abstractmethod
    def renderizar_header(self):
        """Renderiza el encabezado"""
        pass
    
    @abstractmethod
    def renderizar_contenido(self, filtros: FilterConfig):
        """Renderiza el contenido principal"""
        pass
    
    def aplicar_filtros_sidebar(self) -> FilterConfig:
        """Renderiza filtros en sidebar"""
        fecha_min, fecha_max = self.repo.get_date_range()
        
        st.sidebar.header("🔍 Filtros")
        
        fecha_inicio = st.sidebar.date_input(
            "Fecha Inicio",
            value=fecha_min,
            min_value=fecha_min,
            max_value=fecha_max
        )
        
        fecha_fin = st.sidebar.date_input(
            "Fecha Fin",
            value=fecha_max,
            min_value=fecha_min,
            max_value=fecha_max
        )
        
        areas = self.repo.get_areas()
        area = st.sidebar.selectbox("Área", ["Todas"] + areas)
        
        return FilterConfig(
            fecha_inicio=pd.to_datetime(fecha_inicio),
            fecha_fin=pd.to_datetime(fecha_fin),
            area=area if area != "Todas" else None
        )
    
    def render(self):
        """Template method que orquesta el renderizado"""
        self.renderizar_header()
        filtros = self.aplicar_filtros_sidebar()
        self.renderizar_contenido(filtros)

# ============================================
# EXPORTS
# ============================================

__all__ = [
    'MetricConfig',
    'FilterConfig',
    'ChartConfig',
    'DataRepository',
    'ChartStrategy',
    'ChartStrategyFactory',
    'MetricService',
    'ComponentFactory',
    'BasePage'
]