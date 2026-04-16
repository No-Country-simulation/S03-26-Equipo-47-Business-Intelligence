"""
💰 Página Financiero - Refactorizada
Análisis de métricas financieras usando arquitectura limpia
"""

import streamlit as st
import pandas as pd
from core import BasePage, FilterConfig, MetricService, ChartConfig, ChartStrategyFactory, ComponentFactory
from core.repository import RepositoryFactory

class FinancieroPage(BasePage):
    """Página de análisis financiero"""
    
    # IDs de métricas financieras
    ID_INGRESOS = 1
    ID_COSTOS = 2
    ID_GASTOS = 3
    
    def configurar_pagina(self):
        st.set_page_config(
            page_title="Financiero | Sustainable Growth",
            page_icon="💰",
            layout="wide"
        )
    
    def renderizar_header(self):
        st.title("💰 Análisis Financiero")
        st.markdown("""
        Monitoreo integral de métricas económicas: ingresos, costos y gastos operativos.
        """)
        st.markdown("---")
    
    def renderizar_contenido(self, filtros: FilterConfig):
        # Aplicar filtro de categoría financiera
        filtros.categoria = 'Financiera'
        
        # Obtener datos
        df = self.repo.get_fact_monitoreo(filtros)
        
        if df.empty:
            st.warning("⚠️ No hay datos disponibles para el período seleccionado")
            return
        
        # KPIs Principales
        self._renderizar_kpis(df)
        
        st.markdown("---")
        
        # Evolución Temporal
        self._renderizar_evolucion_temporal(filtros)
        
        st.markdown("---")
        
        # Análisis Comparativo
        self._renderizar_comparativo(filtros)
        
        st.markdown("---")
        
        # Margen Operativo
        self._renderizar_margen_operativo(filtros)
    
    def _renderizar_kpis(self, df: pd.DataFrame):
        """Renderiza KPIs principales"""
        st.header("📊 Indicadores Clave")
        
        # Obtener último y penúltimo período
        fecha_ultimo = df['fecha'].max()
        fecha_anterior = df[df['fecha'] < fecha_ultimo]['fecha'].max()
        
        df_ultimo = df[df['fecha'] == fecha_ultimo]
        df_anterior = df[df['fecha'] == fecha_anterior] if not pd.isna(fecha_anterior) else pd.DataFrame()
        
        with st.container(horizontal=True):
            for id_metrica in [self.ID_INGRESOS, self.ID_COSTOS, self.ID_GASTOS]:
                metrica_actual = df_ultimo[df_ultimo['id_metrica'] == id_metrica]
                metrica_anterior = df_anterior[df_anterior['id_metrica'] == id_metrica] if not df_anterior.empty else pd.DataFrame()
                
                if not metrica_actual.empty:
                    valor_actual = metrica_actual['valor'].iloc[0]
                    nombre = metrica_actual['metrica'].iloc[0]
                    unidad = metrica_actual['unidad'].iloc[0]
                    
                    # Calcular variación
                    variacion = None
                    if not metrica_anterior.empty:
                        valor_anterior = metrica_anterior['valor'].iloc[0]
                        if valor_anterior != 0:
                            variacion = ((valor_actual - valor_anterior) / valor_anterior) * 100
                    
                    ComponentFactory.crear_kpi_card(nombre, valor_actual, unidad, variacion)
    
    def _renderizar_evolucion_temporal(self, filtros: FilterConfig):
        """Renderiza evolución temporal de las métricas"""
        st.header("📈 Evolución Temporal")
        
        tab1, tab2, tab3 = st.tabs(["💵 Ingresos", "💸 Costos", "👥 Gastos de Personal"])
        
        with tab1:
            self._renderizar_metrica(self.ID_INGRESOS, "Evolución de Ingresos", filtros, 'linea', '#1f77b4')
        
        with tab2:
            self._renderizar_metrica(self.ID_COSTOS, "Evolución de Costos", filtros, 'barras', '#ff7f0e')
        
        with tab3:
            self._renderizar_metrica(self.ID_GASTOS, "Evolución de Gastos", filtros, 'area', '#2ca02c')
    
    def _renderizar_metrica(self, id_metrica: int, titulo: str, filtros: FilterConfig, 
                           tipo_grafico: str, color: str):
        """Renderiza una métrica individual con gráfico y estadísticas"""
        with st.container(border=True):
            # Obtener evolución
            df_evolucion = self.metric_service.get_evolucion_mensual(id_metrica, filtros)
            
            if df_evolucion.empty:
                st.info(f"No hay datos para esta métrica")
                return
            
            # Obtener metadatos
            metricas = self.repo.get_metricas()
            metrica = next((m for m in metricas if m.id == id_metrica), None)
            unidad = metrica.unidad if metrica else ''
            
            # Crear gráfico
            config = ChartConfig(
                titulo=titulo,
                tipo=tipo_grafico,
                color=color
            )
            
            strategy = ChartStrategyFactory.get_strategy(tipo_grafico)
            fig = strategy.crear_grafico(df_evolucion, config)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Estadísticas
            stats = self.metric_service.calcular_estadisticas(df_evolucion)
            ComponentFactory.crear_seccion_stats(stats, unidad)
    
    def _renderizar_comparativo(self, filtros: FilterConfig):
        """Renderiza análisis comparativo de las 3 métricas"""
        st.header("📊 Análisis Comparativo")
        
        with st.container(border=True):
            st.subheader("Evolución de Métricas Financieras")
            
            # Obtener datos de las 3 métricas
            datos_combinados = []
            
            for id_metrica in [self.ID_INGRESOS, self.ID_COSTOS, self.ID_GASTOS]:
                df = self.metric_service.get_evolucion_mensual(id_metrica, filtros)
                if not df.empty:
                    metricas = self.repo.get_metricas()
                    metrica = next((m for m in metricas if m.id == id_metrica), None)
                    df['metrica'] = metrica.nombre if metrica else f'Métrica {id_metrica}'
                    datos_combinados.append(df)
            
            if datos_combinados:
                import plotly.express as px
                
                df_combined = pd.concat(datos_combinados, ignore_index=True)
                
                fig = px.line(
                    df_combined,
                    x='fecha',
                    y='valor',
                    color='metrica',
                    title='Comparación de Métricas Financieras',
                    markers=True
                )
                
                fig.update_layout(
                    height=400,
                    xaxis_title='',
                    yaxis_title='Valor (ARS)',
                    hovermode='x unified',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.info("💡 **Insight**: Analiza cómo evolucionan tus ingresos en relación con costos y gastos.")
    
    def _renderizar_margen_operativo(self, filtros: FilterConfig):
        """Renderiza análisis de margen operativo"""
        st.header("💹 Margen Operativo")
        
        with st.container(border=True):
            st.markdown("""
            **Margen Operativo** = (Ingresos - Costos - Gastos) / Ingresos × 100
            
            Mide la rentabilidad operativa del negocio.
            """)
            
            # Obtener datos
            df_ingresos = self.metric_service.get_evolucion_mensual(self.ID_INGRESOS, filtros)
            df_costos = self.metric_service.get_evolucion_mensual(self.ID_COSTOS, filtros)
            df_gastos = self.metric_service.get_evolucion_mensual(self.ID_GASTOS, filtros)
            
            if not df_ingresos.empty and not df_costos.empty and not df_gastos.empty:
                # Calcular margen
                df_margen = df_ingresos.copy()
                df_margen = df_margen.merge(df_costos, on='fecha', suffixes=('_ing', '_cost'))
                df_margen = df_margen.merge(df_gastos, on='fecha')
                df_margen.columns = ['fecha', 'ingresos', 'costos', 'gastos']
                
                df_margen['margen_operativo'] = (
                    (df_margen['ingresos'] - df_margen['costos'] - df_margen['gastos']) / 
                    df_margen['ingresos']
                ) * 100
                
                # Gráfico
                config = ChartConfig(
                    titulo='Evolución del Margen Operativo',
                    tipo='linea',
                    color='#9467bd',
                    mostrar_objetivo=True,
                    valor_objetivo=12
                )
                
                df_plot = df_margen[['fecha', 'margen_operativo']].rename(columns={'margen_operativo': 'valor'})
                
                strategy = ChartStrategyFactory.get_strategy('linea')
                fig = strategy.crear_grafico(df_plot, config)
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Métricas
                margen_actual = df_margen.iloc[-1]['margen_operativo']
                margen_promedio = df_margen['margen_operativo'].mean()
                margen_mejor = df_margen['margen_operativo'].max()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Margen Actual", f"{margen_actual:.1f}%", border=True)
                
                with col2:
                    st.metric("Margen Promedio", f"{margen_promedio:.1f}%", border=True)
                
                with col3:
                    st.metric("Mejor Margen", f"{margen_mejor:.1f}%", border=True)
                
                # Interpretación
                if margen_actual >= 12:
                    st.success("✅ Excelente margen operativo")
                elif margen_actual >= 5:
                    st.warning("⚠️ Margen aceptable, pero mejorable")
                else:
                    st.error("🔴 Margen bajo. Acciones correctivas requeridas")
            else:
                st.warning("Se requieren datos de ingresos, costos y gastos para calcular el margen")

def main():
    repo = RepositoryFactory.create(tipo="duckdb", db_path="database/technova.duckdb")
    service = MetricService(repo)
    page = FinancieroPage(repo, service)
    page.render()

if __name__ == "__main__":
    main()