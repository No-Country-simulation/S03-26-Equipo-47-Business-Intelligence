"""
🏠 Home - Página de Bienvenida
Arquitectura refactorizada con patrones de diseño
"""

import streamlit as st
from core import BasePage, FilterConfig, MetricService
from core.repository import RepositoryFactory

class HomePage(BasePage):
    """Página de bienvenida"""
    
    def configurar_pagina(self):
        st.set_page_config(
            page_title="Sustainable Growth Monitor",
            page_icon="🌱",
            layout="wide"
        )
    
    def renderizar_header(self):
        st.title("🌱 Sustainable Growth Monitor")
        st.markdown("""
        ### Dashboard de Sostenibilidad y Rentabilidad para PyMEs
        
        Monitorea el desempeño integral de tu negocio combinando métricas financieras 
        con indicadores ESG (Environmental, Social, Governance).
        """)
        st.markdown("---")
    
    def renderizar_contenido(self, filtros: FilterConfig):
        # Características
        st.header("✨ Características Principales")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            with st.container(border=True):
                st.markdown("### 💰 Análisis Financiero")
                st.markdown("""
                - Ingresos, costos y gastos
                - Margen operativo
                - Tendencias y proyecciones
                """)
        
        with col2:
            with st.container(border=True):
                st.markdown("### 🌍 Impacto Ambiental")
                st.markdown("""
                - Consumo energético
                - Gestión de residuos
                - Intensidad energética
                """)
        
        with col3:
            with st.container(border=True):
                st.markdown("### 👥 Bienestar Social")
                st.markdown("""
                - Satisfacción laboral
                - Capacitación
                - Seguridad e higiene
                """)
        
        st.markdown("---")
        
        # Navegación
        st.header("🧭 Explora el Dashboard")
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.container(border=True):
                st.markdown("### 📈 Análisis por Dimensión")
                st.markdown("""
                - **💰 Financiero:** Ingresos, costos, rentabilidad
                - **🌍 Ambiental:** Energía, residuos, eficiencia
                - **👥 Social:** Satisfacción, capacitación, seguridad
                """)
        
        with col2:
            with st.container(border=True):
                st.markdown("### 🔗 Análisis Avanzado")
                st.markdown("""
                - **Correlaciones:** Relaciones entre variables
                - **Alertas:** Sistema proactivo de monitoreo
                """)
        
        st.markdown("---")
        st.caption("🌱 Sustainable Growth Monitor | Dashboard de Sostenibilidad")
    
    def aplicar_filtros_sidebar(self) -> FilterConfig:
        st.sidebar.markdown("### 🧭 Navegación")
        st.sidebar.info("""
        Usa el menú lateral para navegar entre secciones.
        """)
        
        fecha_min, fecha_max = self.repo.get_date_range()
        return FilterConfig(fecha_inicio=fecha_min, fecha_fin=fecha_max)

def main():
    repo = RepositoryFactory.create(tipo="duckdb", db_path="database/technova.duckdb")
    service = MetricService(repo)
    page = HomePage(repo, service)
    page.render()

if __name__ == "__main__":
    main()