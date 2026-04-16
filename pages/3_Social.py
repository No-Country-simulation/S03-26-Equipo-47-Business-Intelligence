"""
👥 Página Social - Refactorizada
"""

import streamlit as st
import pandas as pd
from core import BasePage, FilterConfig, MetricService, ChartConfig, ChartStrategyFactory, ComponentFactory
from core.repository import RepositoryFactory

class SocialPage(BasePage):
    
    ID_SATISFACCION = 6
    ID_CAPACITACION = 7
    ID_ACCIDENTES = 8
    
    def configurar_pagina(self):
        st.set_page_config(
            page_title="Social | Sustainable Growth",
            page_icon="👥",
            layout="wide"
        )
    
    def renderizar_header(self):
        st.title("👥 Análisis Social (S)")
        st.markdown("Monitoreo del bienestar del equipo: satisfacción laboral, desarrollo profesional y seguridad.")
        st.markdown("---")
    
    def renderizar_contenido(self, filtros: FilterConfig):
        filtros.categoria = 'S'
        
        df = self.repo.get_fact_monitoreo(filtros)
        
        if df.empty:
            st.warning("⚠️ No hay datos disponibles")
            return
        
        self._renderizar_kpis(df)
        st.markdown("---")
        
        tab1, tab2, tab3 = st.tabs(["😊 Satisfacción", "📚 Capacitación", "🏥 Seguridad"])
        
        with tab1:
            self._renderizar_satisfaccion(filtros)
        
        with tab2:
            self._renderizar_capacitacion(filtros)
        
        with tab3:
            self._renderizar_seguridad(filtros)
        
        st.markdown("---")
        self._renderizar_equipo()
    
    def _renderizar_kpis(self, df: pd.DataFrame):
        st.header("📊 Indicadores Sociales Clave")
        
        fecha_ultimo = df['fecha'].max()
        fecha_anterior = df[df['fecha'] < fecha_ultimo]['fecha'].max()
        
        df_ultimo = df[df['fecha'] == fecha_ultimo]
        df_anterior = df[df['fecha'] == fecha_anterior] if not pd.isna(fecha_anterior) else pd.DataFrame()
        
        with st.container(horizontal=True):
            for id_metrica in [self.ID_SATISFACCION, self.ID_CAPACITACION, self.ID_ACCIDENTES]:
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
    
    def _renderizar_satisfaccion(self, filtros: FilterConfig):
        with st.container(border=True):
            st.subheader("Evolución de Satisfacción Laboral")
            
            df_evolucion = self.metric_service.get_evolucion_mensual(self.ID_SATISFACCION, filtros)
            
            if df_evolucion.empty:
                st.info("No hay datos de satisfacción")
                return
            
            config = ChartConfig(
                titulo='Satisfacción Laboral',
                tipo='linea',
                color='#ff7f0e',
                mostrar_objetivo=True,
                valor_objetivo=7.5
            )
            
            strategy = ChartStrategyFactory.get_strategy('linea')
            fig = strategy.crear_grafico(df_evolucion, config)
            
            st.plotly_chart(fig, use_container_width=True)
            
            stats = self.metric_service.calcular_estadisticas(df_evolucion)
            ComponentFactory.crear_seccion_stats(stats, 'puntos')
            
            satisfaccion_actual = df_evolucion.iloc[-1]['valor']
            if satisfaccion_actual >= 8.5:
                st.success("🌟 Excelente clima laboral")
            elif satisfaccion_actual >= 7.5:
                st.info("👍 Buen nivel de satisfacción")
            else:
                st.warning("⚠️ Se requieren mejoras")
    
    def _renderizar_capacitacion(self, filtros: FilterConfig):
        with st.container(border=True):
            st.subheader("Inversión en Capacitación")
            
            df_evolucion = self.metric_service.get_evolucion_mensual(self.ID_CAPACITACION, filtros)
            
            if df_evolucion.empty:
                st.info("No hay datos de capacitación")
                return
            
            config = ChartConfig(
                titulo='Horas de Capacitación por Mes',
                tipo='barras',
                color='#9467bd'
            )
            
            strategy = ChartStrategyFactory.get_strategy('barras')
            fig = strategy.crear_grafico(df_evolucion, config)
            
            st.plotly_chart(fig, use_container_width=True)
            
            stats = self.metric_service.calcular_estadisticas(df_evolucion)
            ComponentFactory.crear_seccion_stats(stats, 'horas')
    
    def _renderizar_seguridad(self, filtros: FilterConfig):
        with st.container(border=True):
            st.subheader("Días de Baja por Accidentes")
            
            df_evolucion = self.metric_service.get_evolucion_mensual(self.ID_ACCIDENTES, filtros)
            
            if df_evolucion.empty:
                st.info("No hay datos de accidentes")
                return
            
            config = ChartConfig(
                titulo='Días de Baja por Accidentes - Mensual',
                tipo='barras',
                color='#d62728',
                mostrar_objetivo=True,
                valor_objetivo=3
            )
            
            strategy = ChartStrategyFactory.get_strategy('barras')
            fig = strategy.crear_grafico(df_evolucion, config)
            
            st.plotly_chart(fig, use_container_width=True)
            
            stats = self.metric_service.calcular_estadisticas(df_evolucion)
            ComponentFactory.crear_seccion_stats(stats, 'días')
    
    def _renderizar_equipo(self):
        st.header("👥 Composición del Equipo")
        
        df_empleados = self.repo.get_empleados()
        
        if df_empleados.empty:
            st.info("No hay información de empleados")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.container(border=True):
                st.subheader("Distribución por Área")
                
                import plotly.express as px
                
                area_counts = df_empleados['area'].value_counts().reset_index()
                area_counts.columns = ['area', 'cantidad']
                
                fig = px.pie(
                    area_counts,
                    values='cantidad',
                    names='area',
                    title='Empleados por Área',
                    hole=0.4
                )
                
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            with st.container(border=True):
                st.subheader("Métricas del Equipo")
                
                total_empleados = len(df_empleados)
                num_areas = df_empleados['area'].nunique()
                
                st.metric("Total Empleados", total_empleados, border=True)
                st.metric("Áreas", num_areas, border=True)
                
                if 'genero' in df_empleados.columns:
                    genero_counts = df_empleados['genero'].value_counts()
                    if len(genero_counts) >= 2:
                        diversidad = min(genero_counts.values) / max(genero_counts.values) * 100
                        st.metric("Índice de Diversidad", f"{diversidad:.0f}%", border=True)

def main():
    repo = RepositoryFactory.create(tipo="duckdb", db_path="database/technova.duckdb")
    service = MetricService(repo)
    page = SocialPage(repo, service)
    page.render()

if __name__ == "__main__":
    main()