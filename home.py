"""
🌱 Sustainable Growth Monitor - Home
Página de Bienvenida
"""

import streamlit as st
from pathlib import Path

# ============================================
# CONFIGURACIÓN DE PÁGINA
# ============================================

st.set_page_config(
    page_title="Sustainable Growth Monitor",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# ESTILOS PERSONALIZADOS
# ============================================

st.markdown("""
    <style>
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
    }
    .medium-font {
        font-size: 18px !important;
    }
    .highlight-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2ca02c;
    }
    .feature-box {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================

# Logo y título
col1, col2 = st.columns([1, 4])

with col1:
    st.markdown("# 🌱")

with col2:
    st.title("Sustainable Growth Monitor")
    st.markdown("**Panel Inteligente de Sostenibilidad y Rentabilidad para PyMEs**")

st.markdown("---")

# ============================================
# INTRODUCCIÓN
# ============================================

st.markdown("""
<div>
    <h2>¿Qué es Sustainable Growth Monitor?</h2>
    <p style="font-size: 18px;">
    Una plataforma integral que combina <strong>inteligencia financiera</strong> y <strong>sostenibilidad ESG</strong> 
    en un único panel de control. Diseñada específicamente para PyMEs que quieren crecer de forma 
    <strong>rentable</strong> y <strong>responsable</strong>.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("")

# ============================================
# PROBLEMA Y SOLUCIÓN
# ============================================

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎯 El Desafío")
    st.markdown("""
    Las PyMEs enfrentan múltiples retos:
    
    - 📊 **Datos dispersos** en múltiples sistemas
    - 💰 **Falta de visibilidad** de impacto ambiental vs rentabilidad
    - 🌍 **Presión regulatoria** creciente en ESG
    - ⏱️ **Poco tiempo** para análisis complejos
    - 📈 **Dificultad** para tomar decisiones basadas en datos
    """)

with col2:
    st.markdown("### ✅ Nuestra Solución")
    st.markdown("""
    Un dashboard que **integra todo**:
    
    - 📈 **KPIs financieros** en tiempo real
    - 🌱 **Métricas ambientales** (energía, reciclaje)
    - 👥 **Indicadores sociales** (satisfacción, capacitación)
    - 🔗 **Correlaciones inteligentes** entre variables
    - ⚠️ **Alertas automáticas** y recomendaciones
    """)

st.markdown("---")

# ============================================
# CARACTERÍSTICAS PRINCIPALES
# ============================================

st.markdown("## 🚀 ¿Qué puedes hacer en esta plataforma?")

# Características en tarjetas
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("### 💰 Análisis Financiero")
        st.markdown("""
        **Monitorea tu salud económica:**
        - Ingresos y costos en tiempo real
        - Gastos operativos y de personal
        - Tendencias y variaciones mensuales
        - Identificación de oportunidades de ahorro
        """)
        st.success("📊 Visibilidad total de tu rentabilidad")

with col2:
    with st.container(border=True):
        st.markdown("### 🌍 Impacto Ambiental")
        st.markdown("""
        **Mide tu huella ecológica:**
        - Consumo energético detallado
        - Tasa de reciclaje por área
        - Eficiencia energética vs ingresos
        - Cumplimiento de objetivos verdes
        """)
        st.success("🌱 Sostenibilidad medible y accionable")

with col3:
    with st.container(border=True):
        st.markdown("### 👥 Bienestar Social")
        st.markdown("""
        **Cuida a tu equipo:**
        - Satisfacción laboral continua
        - Inversión en capacitación
        - Seguridad y días de baja
        - Clima organizacional
        """)
        st.success("😊 Equipo feliz, empresa exitosa")

st.markdown("")

# Segunda fila de características
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("### 🔗 Correlaciones Inteligentes")
        st.markdown("""
        **Descubre relaciones ocultas:**
        - ¿El reciclaje mejora la satisfacción?
        - ¿La eficiencia energética aumenta márgenes?
        - ¿La capacitación impacta en productividad?
        - Análisis visual de tendencias
        """)
        st.info("💡 Insights basados en tus datos reales")

with col2:
    with st.container(border=True):
        st.markdown("### ⚠️ Alertas Proactivas")
        st.markdown("""
        **Reacciona antes que sea tarde:**
        - Sistema de semáforo (🔴 🟡 🟢)
        - Detección automática de anomalías
        - Recomendaciones específicas
        - Priorización de acciones
        """)
        st.warning("🔔 Nunca te pierdas una señal crítica")

with col3:
    with st.container(border=True):
        st.markdown("### 📊 Reportes Ejecutivos")
        st.markdown("""
        **Todo lo que necesitas saber:**
        - Comparativas por período
        - Estado ESG consolidado
        - Exportación de datos
        - Filtros dinámicos personalizables
        """)
        st.success("📈 Decisiones informadas, resultados medibles")

st.markdown("---")

# ============================================
# MÉTRICAS MONITOREADAS
# ============================================

st.markdown("## 📊 Métricas Monitoreadas")

tab1, tab2, tab3 = st.tabs(["💰 Financiero", "🌍 Ambiental (E)", "👥 Social (S)"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### Métricas Clave
        
        | Métrica | Unidad | Frecuencia |
        |---------|--------|------------|
        | 💵 Ingresos Totales | ARS | Mensual |
        | 💸 Costo de Compras | ARS | Mensual |
        | 👥 Gasto de Personal | ARS | Mensual |
        """)
    
    with col2:
        st.markdown("""
        #### Indicadores Derivados
        
        - **Margen Bruto**: Rentabilidad antes de gastos operativos
        - **EBITDA**: Generación de caja operativa
        - **Margen Neto**: Rentabilidad final del negocio
        - **Productividad**: Ingresos por empleado
        """)

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### Métricas Clave
        
        | Métrica | Unidad | Frecuencia |
        |---------|--------|------------|
        | ⚡ Consumo Energético | kWh | Mensual |
        | ♻️ Tasa de Reciclaje | % | Mensual |
        | 🌡️ Huella de Carbono | tCO2e | Mensual |
        """)
    
    with col2:
        st.markdown("""
        #### Objetivos Ambientales
        
        - **Reducción Energética**: -8% anual
        - **Meta de Reciclaje**: >60% residuos
        - **Intensidad Energética**: Optimizar kWh/ARS
        - **Energías Renovables**: Incrementar adopción
        """)

with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### Métricas Clave
        
        | Métrica | Unidad | Frecuencia |
        |---------|--------|------------|
        | 😊 Satisfacción Laboral | pts (1-10) | Trimestral |
        | 📚 Horas Capacitación | horas | Mensual |
        | 🏥 Días Baja Accidentes | días | Mensual |
        """)
    
    with col2:
        st.markdown("""
        #### Objetivos Sociales
        
        - **Satisfacción**: Mantener >7.5 puntos
        - **Capacitación**: >20 horas/empleado/año
        - **Seguridad**: Tender a 0 accidentes
        - **Rotación**: Mantener <10% anual
        """)

st.markdown("---")

# ============================================
# CÓMO NAVEGAR
# ============================================

st.markdown("## 🧭 Navegación de la Plataforma")

st.info("""
👈 **Usa el menú lateral** para acceder a cada sección:

- **🏠 Home**: Esta página de bienvenida
- **💰 Financiero**: Análisis profundo de métricas económicas
- **🌍 Ambiental**: Monitoreo de impacto ecológico
- **👥 Social**: Indicadores de bienestar del equipo
- **🔗 Correlaciones**: Análisis cruzado de variables
- **⚠️ Alertas**: Sistema de alertas y recomendaciones
""")

# ============================================
# CASO DE USO EJEMPLO
# ============================================

st.markdown("## 💡 Caso de Uso Real")

with st.expander("📖 Cómo TechNova aumentó su rentabilidad un 15% mejorando su sostenibilidad"):
    st.markdown("""
    ### El Contexto
    
    **TechNova** es una PyME tecnológica de 25 empleados que enfrentaba:
    - 📉 Márgenes decrecientes por aumento de costos energéticos
    - 😟 Baja satisfacción laboral (6.5/10)
    - ♻️ Apenas 35% de reciclaje
    
    ### Las Acciones
    
    Usando Sustainable Growth Monitor, identificaron:
    
    1. **Correlación clave**: El consumo energético representaba el 18% de costos operativos
    2. **Oportunidad**: Implementar paneles solares y optimizar horarios
    3. **Insight social**: Los empleados valoraban las iniciativas verdes
    
    ### Los Resultados (12 meses)
    
    ✅ **Financiero**
    - Reducción de costos energéticos: -22%
    - Aumento de margen neto: +15%
    - ROI de inversión verde: 18 meses
    
    ✅ **Ambiental**
    - Consumo energético: -28%
    - Tasa de reciclaje: 72%
    - Reducción huella de carbono: -31%
    
    ✅ **Social**
    - Satisfacción laboral: 8.2/10
    - Rotación de personal: -40%
    - Compromiso con empresa: +35%
    """)

st.markdown("---")

# ============================================
# PRÓXIMOS PASOS
# ============================================

st.markdown("## 🎯 Comienza Ahora")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 1️⃣ Explora")
    st.markdown("""
    Navega por las diferentes secciones usando el menú lateral.
    Cada página ofrece visualizaciones y análisis específicos.
    """)

with col2:
    st.markdown("### 2️⃣ Filtra")
    st.markdown("""
    Usa los filtros de fecha, categoría y área para personalizar
    tu análisis según tus necesidades específicas.
    """)

with col3:
    st.markdown("### 3️⃣ Actúa")
    st.markdown("""
    Revisa las alertas y recomendaciones automáticas para
    tomar decisiones informadas y oportunas.
    """)

st.markdown("---")

# ============================================
# FOOTER
# ============================================

st.markdown("### 📚 Recursos Adicionales")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("📄 **Documentación**")
    st.caption("Guías de uso completas")

with col2:
    st.markdown("🎓 **Tutoriales**")
    st.caption("Videos paso a paso")

with col3:
    st.markdown("💬 **Soporte**")
    st.caption("Ayuda técnica")

with col4:
    st.markdown("🔄 **Actualizaciones**")
    st.caption("Novedades mensuales")

st.markdown("---")

st.markdown("")
st.caption("🌱 Sustainable Growth Monitor | v1.0 | Desarrollado para PyMEs sostenibles y rentables")