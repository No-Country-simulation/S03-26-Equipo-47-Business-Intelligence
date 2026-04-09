"""
🔗 Página Correlaciones
Análisis cruzado de variables ESG y financieras
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

# Importar utilidades
from utils.database import load_fact_monitoreo, get_date_range
from utils.config import formatear_valor
from utils.analytics import (
    calcular_correlacion,
    interpretar_correlacion,
    calcular_intensidad_energetica
)
from utils.components import (
    render_filtros_sidebar,
    render_grafico_correlacion
)

# ============================================
# CONFIGURACIÓN DE PÁGINA
# ============================================

st.set_page_config(
    page_title="Correlaciones | Sustainable Growth",
    page_icon="🔗",
    layout="wide"
)

# ============================================
# HEADER
# ============================================

st.title("🔗 Análisis de Correlaciones")
st.markdown("""
Descubre relaciones ocultas entre variables ESG y financieras.
¿La sostenibilidad impacta en la rentabilidad? ¿El bienestar del equipo mejora los resultados?
""")

st.markdown("---")

# ============================================
# CARGAR DATOS
# ============================================

try:
    fecha_min, fecha_max = get_date_range()
    
    # Cargar todos los datos
    df_todos = load_fact_monitoreo()
    
    # Aplicar filtros desde sidebar
    fecha_inicio, fecha_fin, _, area_seleccionada = render_filtros_sidebar(
        df_todos,
        mostrar_area=True,
        mostrar_categoria=True
    )
    
    # Filtrar datos
    df_filtrado = load_fact_monitoreo(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        area=area_seleccionada if area_seleccionada != 'Todas' else None
    )
    
    if df_filtrado.empty:
        st.warning("⚠️ No hay datos disponibles para el período seleccionado")
        st.stop()

except Exception as e:
    st.error(f"❌ Error al cargar datos: {e}")
    st.info("💡 Verifica que la base de datos esté configurada correctamente")
    st.stop()

# ============================================
# SELECTOR DE ANÁLISIS
# ============================================

st.header("🎯 Selecciona el Análisis de Correlación")

# Análisis predefinidos
analisis_options = [
    "💰 Consumo Energético vs Ingresos",
    "♻️ Tasa de Reciclaje vs Satisfacción Laboral",
    "📚 Capacitación vs Ingresos",
    "😊 Satisfacción vs Productividad",
    "⚡ Eficiencia Energética vs Margen",
    "🎨 Análisis Personalizado"
]

analisis_seleccionado = st.selectbox(
    "Elige un análisis de correlación:",
    analisis_options
)

st.markdown("---")

# ============================================
# ANÁLISIS 1: CONSUMO ENERGÉTICO VS INGRESOS
# ============================================

if analisis_seleccionado == "💰 Consumo Energético vs Ingresos":
    st.header("⚡💰 Consumo Energético vs Ingresos")
    
    st.markdown("""
    **Pregunta clave:** ¿Existe relación entre el consumo energético y los ingresos?
    
    **Hipótesis:** Un aumento en la actividad comercial (ingresos) debería correlacionar con
    mayor consumo energético. Sin embargo, una relación cada vez más débil podría indicar
    mejoras en eficiencia energética.
    """)
    
    with st.container(border=True):
        # Obtener datos
        df_energia = df_filtrado[df_filtrado['id_metrica'] == 4].copy()
        df_ingresos = df_filtrado[df_filtrado['id_metrica'] == 1].copy()
        
        if not df_energia.empty and not df_ingresos.empty:
            # Agregar por mes
            df_energia_m = df_energia.groupby(['anio', 'mes']).agg({'valor': 'sum'}).reset_index()
            df_energia_m.columns = ['anio', 'mes', 'energia']
            
            df_ingresos_m = df_ingresos.groupby(['anio', 'mes']).agg({'valor': 'sum'}).reset_index()
            df_ingresos_m.columns = ['anio', 'mes', 'ingresos']
            
            # Merge
            df_merged = pd.merge(df_energia_m, df_ingresos_m, on=['anio', 'mes'])
            
            if len(df_merged) >= 3:
                # Calcular correlación
                corr, p_valor = calcular_correlacion(
                    df_energia[['anio', 'mes', 'valor']],
                    df_ingresos[['anio', 'mes', 'valor']]
                )
                
                # Gráfico de dispersión
                fig = px.scatter(
                    df_merged,
                    x='energia',
                    y='ingresos',
                    trendline='ols',
                    labels={
                        'energia': 'Consumo Energético (kWh)',
                        'ingresos': 'Ingresos (ARS)'
                    },
                    title='Relación entre Consumo Energético e Ingresos'
                )
                
                fig.update_layout(height=400)
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Interpretación
                categoria, descripcion, emoji = interpretar_correlacion(corr)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Coeficiente de Correlación", f"{corr:.3f}" if corr else "N/A", border=True)
                
                with col2:
                    st.metric("Interpretación", categoria, border=True)
                
                with col3:
                    st.metric("P-valor", f"{p_valor:.4f}" if p_valor else "N/A", border=True)
                
                # Análisis detallado
                st.markdown("#### 📊 Análisis")
                
                if corr and corr > 0.7:
                    st.success(f"""
                    {emoji} **{descripcion}**
                    
                    Existe una fuerte relación positiva entre el consumo energético y los ingresos.
                    Esto sugiere que:
                    - A mayor actividad comercial, mayor consumo energético
                    - La energía es un recurso crítico para la generación de ingresos
                    - **Oportunidad:** Invertir en eficiencia energética puede reducir costos sin afectar ingresos
                    """)
                elif corr and corr > 0:
                    st.info(f"""
                    {emoji} **{descripcion}**
                    
                    Hay una relación positiva moderada o débil. Esto podría indicar:
                    - Ya se han implementado mejoras en eficiencia energética
                    - Parte de los ingresos provienen de actividades de bajo consumo energético
                    - **Oportunidad:** Seguir optimizando el uso de energía
                    """)
                else:
                    st.warning(f"""
                    {emoji} **{descripcion}**
                    
                    La correlación es débil o negativa. Posibles explicaciones:
                    - Datos insuficientes o con mucha variabilidad
                    - Cambios estructurales en el negocio
                    """)
                
                # Calcular intensidad energética
                st.markdown("#### ⚡ Intensidad Energética")
                
                try:
                    df_intensidad = calcular_intensidad_energetica(df_energia, df_ingresos)
                    
                    if not df_intensidad.empty:
                        fig2 = px.line(
                            df_intensidad,
                            x='fecha',
                            y='intensidad_energetica',
                            title='Evolución de Intensidad Energética (kWh/ARS)',
                            markers=True
                        )
                        
                        fig2.update_layout(
                            height=300,
                            xaxis_title='',
                            yaxis_title='kWh por ARS de ingreso'
                        )
                        
                        st.plotly_chart(fig2, use_container_width=True)
                        
                        # Tendencia
                        if len(df_intensidad) >= 2:
                            primer_valor = df_intensidad.iloc[0]['intensidad_energetica']
                            ultimo_valor = df_intensidad.iloc[-1]['intensidad_energetica']
                            cambio_pct = ((ultimo_valor - primer_valor) / primer_valor) * 100
                            
                            if cambio_pct < -5:
                                st.success(f"✅ La intensidad energética se redujo {abs(cambio_pct):.1f}% - ¡Mejora en eficiencia!")
                            elif cambio_pct > 5:
                                st.warning(f"⚠️ La intensidad energética aumentó {cambio_pct:.1f}% - Se requiere optimización")
                            else:
                                st.info(f"📊 La intensidad energética se mantiene estable ({cambio_pct:+.1f}%)")
                except Exception as e:
                    st.warning(f"No se pudo calcular intensidad energética: {e}")
            else:
                st.warning("Se requieren al menos 3 períodos para calcular correlación")
        else:
            st.info("No hay suficientes datos de energía o ingresos para este análisis")

# ============================================
# ANÁLISIS 2: RECICLAJE VS SATISFACCIÓN
# ============================================

elif analisis_seleccionado == "♻️ Tasa de Reciclaje vs Satisfacción Laboral":
    st.header("♻️😊 Tasa de Reciclaje vs Satisfacción Laboral")
    
    st.markdown("""
    **Pregunta clave:** ¿Las prácticas sostenibles impactan en el clima laboral?
    
    **Hipótesis:** Empleados de empresas con mejores prácticas ambientales suelen estar
    más satisfechos con su lugar de trabajo. La sostenibilidad puede ser un factor de orgullo y motivación.
    """)
    
    with st.container(border=True):
        # Obtener datos
        df_reciclaje = df_filtrado[df_filtrado['id_metrica'] == 5].copy()
        df_satisfaccion = df_filtrado[df_filtrado['id_metrica'] == 6].copy()
        
        if not df_reciclaje.empty and not df_satisfaccion.empty:
            # Agregar por trimestre (satisfacción es trimestral)
            df_reciclaje_t = df_reciclaje.groupby(['anio', 'trimestre']).agg({'valor': 'mean'}).reset_index()
            df_reciclaje_t.columns = ['anio', 'trimestre', 'reciclaje']
            
            df_satisfaccion_t = df_satisfaccion.groupby(['anio', 'trimestre']).agg({'valor': 'mean'}).reset_index()
            df_satisfaccion_t.columns = ['anio', 'trimestre', 'satisfaccion']
            
            # Merge
            df_merged = pd.merge(df_reciclaje_t, df_satisfaccion_t, on=['anio', 'trimestre'])
            
            if len(df_merged) >= 3:
                # Calcular correlación
                try:
                    corr, p_valor = stats.pearsonr(df_merged['reciclaje'], df_merged['satisfaccion'])
                except:
                    corr, p_valor = None, None
                
                # Gráfico de dispersión
                fig = px.scatter(
                    df_merged,
                    x='reciclaje',
                    y='satisfaccion',
                    trendline='ols',
                    labels={
                        'reciclaje': 'Tasa de Reciclaje (%)',
                        'satisfaccion': 'Satisfacción Laboral (pts)'
                    },
                    title='Relación entre Reciclaje y Satisfacción Laboral',
                    color_discrete_sequence=['#2ca02c']
                )
                
                fig.update_layout(height=400)
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Interpretación
                categoria, descripcion, emoji = interpretar_correlacion(corr)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Coeficiente de Correlación", f"{corr:.3f}" if corr else "N/A", border=True)
                
                with col2:
                    st.metric("Interpretación", categoria, border=True)
                
                with col3:
                    st.metric("Significancia", "Alta" if p_valor and p_valor < 0.05 else "Baja", border=True)
                
                # Análisis detallado
                st.markdown("#### 📊 Análisis")
                
                if corr and corr > 0.5:
                    st.success(f"""
                    {emoji} **{descripcion}**
                    
                    ¡Hallazgo interesante! Las prácticas de reciclaje se correlacionan positivamente con la satisfacción laboral:
                    - Los empleados valoran trabajar en empresas socialmente responsables
                    - La sostenibilidad puede ser un factor de orgullo y pertenencia
                    - **Acción recomendada:** Comunicar y celebrar logros ambientales con el equipo
                    """)
                elif corr and corr > 0:
                    st.info(f"""
                    {emoji} **{descripcion}**
                    
                    Hay una relación positiva aunque no muy fuerte:
                    - Otros factores también influyen en la satisfacción laboral
                    - Las prácticas ambientales son un componente más del clima laboral
                    - **Oportunidad:** Involucrar más al equipo en iniciativas verdes
                    """)
                else:
                    st.warning(f"""
                    {emoji} **{descripcion}**
                    
                    No se observa una correlación clara. Posibles razones:
                    - La satisfacción laboral depende de muchos otros factores
                    - El equipo no está al tanto de las prácticas de reciclaje
                    - **Sugerencia:** Hacer más visible el impacto ambiental de la empresa
                    """)
            else:
                st.warning("Se requieren al menos 3 períodos para calcular correlación")
        else:
            st.info("No hay suficientes datos de reciclaje o satisfacción para este análisis")

# ============================================
# ANÁLISIS 3: CAPACITACIÓN VS INGRESOS
# ============================================

elif analisis_seleccionado == "📚 Capacitación vs Ingresos":
    st.header("📚💰 Inversión en Capacitación vs Ingresos")
    
    st.markdown("""
    **Pregunta clave:** ¿La inversión en desarrollo profesional se traduce en mejores resultados?
    
    **Hipótesis:** Un equipo más capacitado debería ser más productivo y generar mayores ingresos.
    El impacto puede no ser inmediato, pero debería ser visible en el mediano plazo.
    """)
    
    with st.container(border=True):
        df_capacitacion = df_filtrado[df_filtrado['id_metrica'] == 7].copy()
        df_ingresos = df_filtrado[df_filtrado['id_metrica'] == 1].copy()
        
        if not df_capacitacion.empty and not df_ingresos.empty:
            # Agregar por mes
            df_cap_m = df_capacitacion.groupby(['anio', 'mes']).agg({'valor': 'sum'}).reset_index()
            df_cap_m.columns = ['anio', 'mes', 'capacitacion']
            
            df_ing_m = df_ingresos.groupby(['anio', 'mes']).agg({'valor': 'sum'}).reset_index()
            df_ing_m.columns = ['anio', 'mes', 'ingresos']
            
            # Merge
            df_merged = pd.merge(df_cap_m, df_ing_m, on=['anio', 'mes'])
            
            if len(df_merged) >= 3:
                # Calcular correlación
                try:
                    corr, p_valor = stats.pearsonr(df_merged['capacitacion'], df_merged['ingresos'])
                except:
                    corr, p_valor = None, None
                
                # Gráfico
                fig = px.scatter(
                    df_merged,
                    x='capacitacion',
                    y='ingresos',
                    trendline='ols',
                    labels={
                        'capacitacion': 'Horas de Capacitación',
                        'ingresos': 'Ingresos (ARS)'
                    },
                    title='Relación entre Capacitación e Ingresos',
                    color_discrete_sequence=['#9467bd']
                )
                
                fig.update_layout(height=400)
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Métricas
                categoria, descripcion, emoji = interpretar_correlacion(corr)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Correlación", f"{corr:.3f}" if corr else "N/A", border=True)
                
                with col2:
                    st.metric("Interpretación", categoria, border=True)
                
                with col3:
                    # ROI estimado
                    if corr and corr > 0.3:
                        st.metric("ROI Capacitación", "Positivo", border=True)
                    else:
                        st.metric("ROI Capacitación", "Indeterminado", border=True)
                
                # Análisis
                st.markdown("#### 📊 Análisis")
                
                if corr and corr > 0.5:
                    st.success(f"""
                    {emoji} **{descripcion}**
                    
                    ¡Excelente noticia! La inversión en capacitación muestra retorno:
                    - Mayor capacitación se asocia con mayores ingresos
                    - El desarrollo profesional mejora la productividad del equipo
                    - **Acción recomendada:** Mantener o incrementar la inversión en formación
                    """)
                elif corr and corr > 0:
                    st.info(f"""
                    {emoji} **{descripcion}**
                    
                    Hay señales positivas aunque no concluyentes:
                    - El impacto de la capacitación puede tardar en manifestarse
                    - Otros factores también influyen en los ingresos
                    - **Sugerencia:** Hacer seguimiento del impacto a largo plazo
                    """)
                else:
                    st.warning(f"""
                    {emoji} **No se observa correlación directa**
                    
                    Esto no significa que la capacitación no sea valiosa:
                    - El impacto puede ser indirecto (satisfacción, retención)
                    - Se requiere más tiempo para ver resultados
                    - **Continuar invirtiendo** en desarrollo profesional
                    """)
            else:
                st.warning("Se requieren al menos 3 períodos para calcular correlación")
        else:
            st.info("No hay suficientes datos para este análisis")

# ============================================
# ANÁLISIS PERSONALIZADO
# ============================================

elif analisis_seleccionado == "🎨 Análisis Personalizado":
    st.header("🎨 Análisis Personalizado")
    
    st.markdown("Selecciona dos métricas para analizar su correlación:")
    
    # Obtener lista de métricas disponibles
    metricas_disponibles = df_filtrado[['id_metrica', 'metrica', 'unidad']].drop_duplicates()
    metricas_dict = dict(zip(metricas_disponibles['metrica'], metricas_disponibles['id_metrica']))
    
    col1, col2 = st.columns(2)
    
    with col1:
        metrica_x = st.selectbox(
            "Variable X (Independiente):",
            list(metricas_dict.keys()),
            key='metrica_x'
        )
    
    with col2:
        metrica_y = st.selectbox(
            "Variable Y (Dependiente):",
            list(metricas_dict.keys()),
            key='metrica_y'
        )
    
    if metrica_x == metrica_y:
        st.warning("⚠️ Por favor selecciona dos métricas diferentes")
    else:
        with st.container(border=True):
            # Obtener datos
            id_x = metricas_dict[metrica_x]
            id_y = metricas_dict[metrica_y]
            
            df_x = df_filtrado[df_filtrado['id_metrica'] == id_x].copy()
            df_y = df_filtrado[df_filtrado['id_metrica'] == id_y].copy()
            
            if not df_x.empty and not df_y.empty:
                # Agregar por mes
                df_x_m = df_x.groupby(['anio', 'mes']).agg({'valor': 'mean'}).reset_index()
                df_x_m.columns = ['anio', 'mes', 'valor_x']
                
                df_y_m = df_y.groupby(['anio', 'mes']).agg({'valor': 'mean'}).reset_index()
                df_y_m.columns = ['anio', 'mes', 'valor_y']
                
                # Merge
                df_merged = pd.merge(df_x_m, df_y_m, on=['anio', 'mes'])
                
                if len(df_merged) >= 3:
                    # Calcular correlación
                    try:
                        corr, p_valor = stats.pearsonr(df_merged['valor_x'], df_merged['valor_y'])
                    except:
                        corr, p_valor = None, None
                    
                    # Obtener unidades
                    unidad_x = df_x['unidad'].iloc[0]
                    unidad_y = df_y['unidad'].iloc[0]
                    
                    # Gráfico
                    fig = px.scatter(
                        df_merged,
                        x='valor_x',
                        y='valor_y',
                        trendline='ols',
                        labels={
                            'valor_x': f"{metrica_x} ({unidad_x})",
                            'valor_y': f"{metrica_y} ({unidad_y})"
                        },
                        title=f'Correlación: {metrica_x} vs {metrica_y}'
                    )
                    
                    fig.update_layout(height=400)
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Métricas
                    categoria, descripcion, emoji = interpretar_correlacion(corr)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Correlación", f"{corr:.3f}" if corr else "N/A", border=True)
                    
                    with col2:
                        st.metric("Tipo", categoria, border=True)
                    
                    with col3:
                        st.metric("P-valor", f"{p_valor:.4f}" if p_valor else "N/A", border=True)
                    
                    # Interpretación
                    st.markdown("#### 📊 Interpretación")
                    
                    if p_valor and p_valor < 0.05:
                        significancia = "estadísticamente significativa"
                    else:
                        significancia = "no alcanza significancia estadística"
                    
                    st.info(f"""
                    {emoji} **{descripcion}** ({significancia})
                    
                    - Coeficiente de correlación: {corr:.3f if corr else 'N/A'}
                    - P-valor: {p_valor:.4f if p_valor else 'N/A'}
                    - Número de observaciones: {len(df_merged)}
                    
                    **Recuerda:** La correlación no implica causalidad. Otros factores pueden estar influyendo en ambas variables.
                    """)
                else:
                    st.warning("Se requieren al menos 3 períodos para calcular correlación")
            else:
                st.info("No hay suficientes datos para este análisis")

# Resto de análisis (implementar de forma similar)
else:
    st.info(f"Análisis '{analisis_seleccionado}' en desarrollo...")

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.caption("🔗 Análisis de Correlaciones | Sustainable Growth Monitor")
st.caption(f"📊 Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}")
st.caption("💡 Correlación no implica causalidad. Usa estos análisis como punto de partida para investigación más profunda.")