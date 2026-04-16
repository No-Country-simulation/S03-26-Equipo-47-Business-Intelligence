"""
🌍 Página Ambiental - Refactorizada
"""

import streamlit as st
import pandas as pd
from core import BasePage, FilterConfig, MetricService, ChartConfig, ChartStrategyFactory, ComponentFactory
from core.repository import RepositoryFactory

class AmbientalPage(BasePage):
    
    ID_ENERGIA = 4
    ID_RECICLAJE = 5
    
    def configurar_pagina(self):
        st.set_page_config(
            page_title="Ambiental | Sustainable Growth",
            page_icon="🌍",
            layout="wide"
        )
    
    def renderizar_header(self):
        st.title("🌍 Análisis Ambiental (E)")
        st.markdown("Monitoreo de impacto ecológico: consumo energético, gestión de residuos y eficiencia ambiental.")
        st.markdown("---")
    
    def renderizar_contenido(self, filtros: FilterConfig):
        filtros.categoria = 'E'
        
        df = self.repo.get_fact_monitoreo(filtros)
        
        if df.empty:
            st.warning("⚠️ No hay datos disponibles")
            return
        
        self._renderizar_kpis(df)
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["⚡ Consumo Energético", "♻️ Gestión de Residuos"])
        
        with tab1:
            self._renderizar_energia(filtros)
        
        with tab2:
            self._renderizar_reciclaje(filtros)
    
    def _renderizar_kpis(self, df: pd.DataFrame):
        st.header("📊 Indicadores Ambientales Clave")
        
        fecha_ultimo = df['fecha'].max()
        fecha_anterior = df[df['fecha'] < fecha_ultimo]['fecha'].max()
        
        df_ultimo = df[df['fecha'] == fecha_ultimo]
        df_anterior = df[df['fecha'] == fecha_anterior] if not pd.isna(fecha_anterior) else pd.DataFrame()
        
        with st.container(horizontal=True):
            for id_metrica in [self.ID_ENERGIA, self.ID_RECICLAJE]:
                metrica_actual = df_ultimo[df_ultimo['id_metrica'] == id_metrica]
                metrica_anterior = df_anterior[df_anterior['id_metrica'] == id_metrica] if not df_anterior.empty else pd.DataFrame()
                
                if not metrica_actual.empty:
                    valor_actual = metrica_actual['valor'].iloc[0]
                    nombre = metrica_actual['metrica'].iloc[0]
                    unidad = metrica_actual['unidad'].iloc[0]
                    
                    variacion = None
                    if not metrica_anterior.empty:
                        valor_anterior = metrica_anterior['valor'].iloc[0]
                        if valor_anterior != 0:
                            variacion = ((valor_actual - valor_anterior) / valor_anterior) * 100
                    
                    ComponentFactory.crear_kpi_card(nombre, valor_actual, unidad, variacion)
    
    def _renderizar_energia(self, filtros: FilterConfig):
        with st.container(border=True):
            st.subheader("Evolución del Consumo Energético")
            
            df_evolucion = self.metric_service.get_evolucion_mensual(self.ID_ENERGIA, filtros)
            
            if df_evolucion.empty:
                st.info("No hay datos de energía")
                return
            
            config = ChartConfig(
                titulo='Consumo Energético Mensual',
                tipo='area',
                color='#2ca02c',
                mostrar_objetivo=True,
                valor_objetivo=120000
            )
            
            strategy = ChartStrategyFactory.get_strategy('area')
            fig = strategy.crear_grafico(df_evolucion, config)
            
            st.plotly_chart(fig, use_container_width=True)
            
            stats = self.metric_service.calcular_estadisticas(df_evolucion)
            ComponentFactory.crear_seccion_stats(stats, 'kWh')
    
    def _renderizar_reciclaje(self, filtros: FilterConfig):
        with st.container(border=True):
            st.subheader("Tasa de Reciclaje")
            
            df_evolucion = self.metric_service.get_evolucion_mensual(self.ID_RECICLAJE, filtros)
            
            if df_evolucion.empty:
                st.info("No hay datos de reciclaje")
                return
            
            config = ChartConfig(
                titulo='Evolución de la Tasa de Reciclaje',
                tipo='linea',
                color='#17becf',
                mostrar_objetivo=True,
                valor_objetivo=60
            )
            
            strategy = ChartStrategyFactory.get_strategy('linea')
            fig = strategy.crear_grafico(df_evolucion, config)
            
            st.plotly_chart(fig, use_container_width=True)
            
            stats = self.metric_service.calcular_estadisticas(df_evolucion)
            ComponentFactory.crear_seccion_stats(stats, '%')
            
            # Interpretación
            tasa_actual = df_evolucion.iloc[-1]['valor']
            if tasa_actual >= 60:
                st.success("✅ Excelente tasa de reciclaje")
            elif tasa_actual >= 30:
                st.warning("⚠️ Tasa mejorable")
            else:
                st.error("🔴 Tasa crítica")

def main():
    repo = RepositoryFactory.create(tipo="duckdb", db_path="database/technova.duckdb")
    service = MetricService(repo)
    page = AmbientalPage(repo, service)
    page.render()

if __name__ == "__main__":
    main()