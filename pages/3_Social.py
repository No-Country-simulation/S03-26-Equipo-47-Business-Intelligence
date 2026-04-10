"""
👥 Página Social
Análisis de métricas sociales (S)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta

# Importar utilidades
from utils.database import load_fact_monitoreo, get_date_range, load_dim_empleado
from utils.config import (
    calcular_estado_metrica, 
    formatear_valor,
    DESCRIPCIONES_METRICAS,
    METRICAS_POR_CATEGORIA
)
from utils.analytics import calcular_variacion
from utils.components import (
    render_filtros_sidebar,
    render_kpi_card,
    render_info_metrica,
    render_resumen_ejecutivo
)

# ============================================
# CONFIGURACIÓN DE PÁGINA
# ============================================

st.set_page_config(
    page_title="Social | Sustainable Growth",
    page_icon="👥",
    layout="wide"
)

# ============================================
# HEADER
# ============================================

st.title("👥 Análisis Social (S)")
st.markdown("""
Monitoreo del bienestar del equipo: satisfacción laboral, desarrollo profesional y seguridad.
Un equipo feliz y capacitado es clave para el éxito sostenible del negocio.
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
        mostrar_categoria=False
    )
    
    # Filtrar datos sociales
    df_filtrado = load_fact_monitoreo(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        categoria='S',
        area=area_seleccionada if area_seleccionada != 'Todas' else None
    )
    
    if df_filtrado.empty:
        st.warning("⚠️ No hay datos sociales disponibles para el período seleccionado")
        st.stop()
    
    # Cargar datos de empleados
    df_empleados = load_dim_empleado()

except Exception as e:
    st.error(f"❌ Error al cargar datos: {e}")
    st.info("💡 Verifica que la base de datos esté configurada correctamente")
    st.stop()

# ============================================
# RESUMEN EJECUTIVO
# ============================================

render_resumen_ejecutivo(
    df_filtrado[df_filtrado['fecha'] == df_filtrado['fecha'].max()],
    f"{fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}"
)

st.markdown("---")

# ============================================
# KPIS PRINCIPALES
# ============================================

st.header("📊 Indicadores Sociales Clave")

# Obtener valores del último período y período anterior
fecha_ultimo = df_filtrado['fecha'].max()
fecha_anterior = df_filtrado[df_filtrado['fecha'] < fecha_ultimo]['fecha'].max()

df_ultimo = df_filtrado[df_filtrado['fecha'] == fecha_ultimo]
df_anterior = df_filtrado[df_filtrado['fecha'] == fecha_anterior] if not pd.isna(fecha_anterior) else pd.DataFrame()

# IDs de métricas sociales
ids_social = METRICAS_POR_CATEGORIA['S']

# Crear KPI cards
with st.container(horizontal=True):
    for id_metrica in ids_social:
        metrica_actual = df_ultimo[df_ultimo['id_metrica'] == id_metrica]
        metrica_anterior = df_anterior[df_anterior['id_metrica'] == id_metrica] if not df_anterior.empty else pd.DataFrame()
        
        if not metrica_actual.empty:
            valor_actual = metrica_actual['valor'].iloc[0]
            nombre = metrica_actual['metrica'].iloc[0]
            unidad = metrica_actual['unidad'].iloc[0]
            
            # Valor anterior
            valor_anterior = metrica_anterior['valor'].iloc[0] if not metrica_anterior.empty else None
            
            # Serie temporal para sparkline
            serie = df_filtrado[df_filtrado['id_metrica'] == id_metrica].sort_values('fecha')
            chart_data = serie['valor'].tail(10).tolist()
            
            render_kpi_card(
                metrica=nombre,
                valor_actual=valor_actual,
                unidad=unidad,
                valor_anterior=valor_anterior,
                sparkline_data=chart_data,
                id_metrica=id_metrica
            )

st.markdown("---")

# ============================================
# SATISFACCIÓN LABORAL
# ============================================

st.header("😊 Satisfacción Laboral")

tab1, tab2 = st.tabs(["📈 Tendencia", "🏢 Por Área"])

with tab1:
    with st.container(border=True):
        st.subheader("Evolución de la Satisfacción Laboral")
        
        # Datos de satisfacción (id_metrica = 6)
        df_satisfaccion = df_filtrado[df_filtrado['id_metrica'] == 6].copy()
        
        if not df_satisfaccion.empty:
            # Agregar por trimestre (las encuestas son trimestrales)
            df_trimestral = df_satisfaccion.groupby(['anio', 'trimestre']).agg({
                'valor': 'mean'
            }).reset_index()
            df_trimestral['periodo'] = df_trimestral.apply(
                lambda row: f"Q{row['trimestre']} {row['anio']}", axis=1
            )
            
            # Gráfico de línea con rangos
            fig = go.Figure()
            
            # Línea de satisfacción
            fig.add_trace(go.Scatter(
                x=df_trimestral['periodo'],
                y=df_trimestral['valor'],
                mode='lines+markers',
                name='Satisfacción',
                line=dict(color='#ff7f0e', width=3),
                marker=dict(size=10)
            ))
            
            # Rangos de referencia
            fig.add_hrect(y0=8.5, y1=10, fillcolor="green", opacity=0.1, 
                         annotation_text="Excelente", annotation_position="right")
            fig.add_hrect(y0=7.5, y1=8.5, fillcolor="yellow", opacity=0.1,
                         annotation_text="Bueno", annotation_position="right")
            fig.add_hrect(y0=6, y1=7.5, fillcolor="orange", opacity=0.1,
                         annotation_text="Regular", annotation_position="right")
            fig.add_hrect(y0=0, y1=6, fillcolor="red", opacity=0.1,
                         annotation_text="Crítico", annotation_position="right")
            
            fig.update_layout(
                title='Satisfacción Laboral por Trimestre',
                height=350,
                xaxis_title='',
                yaxis_title='Satisfacción (1-10)',
                yaxis_range=[0, 10],
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Estadísticas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                satisfaccion_actual = df_trimestral.iloc[-1]['valor']
                st.metric("Nivel Actual", f"{satisfaccion_actual:.1f} pts", border=True)
            
            with col2:
                satisfaccion_promedio = df_trimestral['valor'].mean()
                st.metric("Promedio del Período", f"{satisfaccion_promedio:.1f} pts", border=True)
            
            with col3:
                mejor_satisfaccion = df_trimestral['valor'].max()
                st.metric("Mejor Nivel", f"{mejor_satisfaccion:.1f} pts", border=True)
            
            with col4:
                # Variación
                if len(df_trimestral) >= 2:
                    primer_valor = df_trimestral.iloc[0]['valor']
                    ultimo_valor = df_trimestral.iloc[-1]['valor']
                    variacion_abs, _ = calcular_variacion(ultimo_valor, primer_valor)
                    st.metric("Evolución", f"{variacion_abs:+.1f} pts", border=True)
            
            # Interpretación
            if satisfaccion_actual >= 8.5:
                st.success("🌟 ¡Excelente clima laboral! El equipo está muy satisfecho.")
            elif satisfaccion_actual >= 7.5:
                st.info("👍 Buen nivel de satisfacción, pero siempre hay espacio para mejorar.")
            elif satisfaccion_actual >= 6:
                st.warning("⚠️ Satisfacción en nivel regular. Se recomienda investigar causas y tomar acciones.")
            else:
                st.error("🔴 Nivel crítico de satisfacción. Se requiere intervención urgente.")
            
            render_info_metrica(6)
        else:
            st.info("No hay datos de satisfacción laboral para el período seleccionado")

with tab2:
    with st.container(border=True):
        st.subheader("Satisfacción por Área")
        
        df_satisfaccion = df_filtrado[df_filtrado['id_metrica'] == 6]
        
        if not df_satisfaccion.empty:
            # Agrupar por área
            df_por_area = df_satisfaccion.groupby('nombre_area').agg({
                'valor': 'mean'
            }).reset_index().sort_values('valor', ascending=True)
            
            # Gráfico de barras horizontales
            fig = px.bar(
                df_por_area,
                x='valor',
                y='nombre_area',
                orientation='h',
                title='Satisfacción Promedio por Área',
                color='valor',
                color_continuous_scale=['red', 'yellow', 'green']
            )
            
            fig.update_layout(
                height=300,
                xaxis_title='Satisfacción (pts)',
                yaxis_title='',
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.info("💡 **Insight**: Identifica áreas con menor satisfacción para focalizar esfuerzos de mejora del clima laboral.")

st.markdown("---")

# ============================================
# DESARROLLO PROFESIONAL
# ============================================

st.header("📚 Desarrollo Profesional")

with st.container(border=True):
    st.subheader("Inversión en Capacitación")
    
    # Datos de capacitación (id_metrica = 7)
    df_capacitacion = df_filtrado[df_filtrado['id_metrica'] == 7].copy()
    
    if not df_capacitacion.empty:
        # Agregar por mes
        df_monthly = df_capacitacion.groupby(['anio', 'mes']).agg({
            'valor': 'sum'
        }).reset_index()
        df_monthly['fecha'] = pd.to_datetime(pd.to_datetime(
                                    df_monthly.rename(columns={
                                        'anio': 'year',
                                        'mes': 'month'
                                    })[['year', 'month']].assign(day=1)
                                ))
        
        # Gráfico de barras
        fig = px.bar(
            df_monthly,
            x='fecha',
            y='valor',
            title='Horas de Capacitación por Mes',
            color_discrete_sequence=['#9467bd']
        )
        
        fig.update_layout(
            height=300,
            xaxis_title='',
            yaxis_title='Horas',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_horas = df_monthly['valor'].sum()
            st.metric("Total Horas", formatear_valor(total_horas, 'horas'), border=True)
        
        with col2:
            promedio_mensual = df_monthly['valor'].mean()
            st.metric("Promedio Mensual", formatear_valor(promedio_mensual, 'horas'), border=True)
        
        with col3:
            # Horas por empleado
            if not df_empleados.empty:
                num_empleados = len(df_empleados)
                horas_por_empleado = total_horas / num_empleados
                st.metric("Horas/Empleado", f"{horas_por_empleado:.1f} hs", border=True)
            else:
                st.metric("Horas/Empleado", "N/A", border=True)
        
        with col4:
            # Objetivo: 20 horas/empleado/año
            if not df_empleados.empty:
                num_empleados = len(df_empleados)
                meses_transcurridos = len(df_monthly)
                horas_esperadas = (20 / 12) * meses_transcurridos * num_empleados
                progreso = (total_horas / horas_esperadas * 100) if horas_esperadas > 0 else 0
                st.metric("vs Objetivo", f"{progreso:.0f}%", border=True)
        
        # Interpretación
        if not df_empleados.empty:
            num_empleados = len(df_empleados)
            horas_por_empleado = total_horas / num_empleados
            
            if horas_por_empleado >= 20:
                st.success("✅ ¡Excelente! Se está superando el objetivo de capacitación.")
            elif horas_por_empleado >= 10:
                st.info("📊 Buen nivel de capacitación, pero se puede mejorar.")
            else:
                st.warning("⚠️ Inversión en capacitación por debajo del objetivo. Se recomienda incrementar.")
        
        render_info_metrica(7)
    else:
        st.info("No hay datos de capacitación para el período seleccionado")

st.markdown("---")

# ============================================
# SEGURIDAD E HIGIENE
# ============================================

st.header("🏥 Seguridad e Higiene")

with st.container(border=True):
    st.subheader("Días de Baja por Accidentes Laborales")
    
    # Datos de accidentes (id_metrica = 8)
    df_accidentes = df_filtrado[df_filtrado['id_metrica'] == 8].copy()
    
    if not df_accidentes.empty:
        # Agregar por mes
        df_monthly = df_accidentes.groupby(['anio', 'mes']).agg({
            'valor': 'sum'
        }).reset_index()
        df_monthly['fecha'] = pd.to_datetime(pd.to_datetime(
                                    df_monthly.rename(columns={
                                        'anio': 'year',
                                        'mes': 'month'
                                    })[['year', 'month']].assign(day=1)
                                ))
        
        # Gráfico de barras con objetivo
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df_monthly['fecha'],
            y=df_monthly['valor'],
            name='Días de Baja',
            marker_color='#d62728'
        ))
        
        # Línea de objetivo (3 días - nivel óptimo)
        fig.add_hline(y=3, line_dash="dash", line_color="green",
                     annotation_text="Objetivo: ≤3 días")
        
        fig.update_layout(
            title='Días de Baja por Accidentes - Mensual',
            height=300,
            xaxis_title='',
            yaxis_title='Días',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_dias = df_monthly['valor'].sum()
            st.metric("Total Días Perdidos", formatear_valor(total_dias, 'días'), border=True)
        
        with col2:
            promedio_mensual = df_monthly['valor'].mean()
            st.metric("Promedio Mensual", formatear_valor(promedio_mensual, 'días'), border=True)
        
        with col3:
            # Meses sin accidentes
            meses_sin_accidentes = len(df_monthly[df_monthly['valor'] == 0])
            st.metric("Meses sin Accidentes", meses_sin_accidentes, border=True)
        
        with col4:
            # Tendencia
            if len(df_monthly) >= 2:
                primer_valor = df_monthly.iloc[0]['valor']
                ultimo_valor = df_monthly.iloc[-1]['valor']
                variacion_abs, _ = calcular_variacion(ultimo_valor, primer_valor)
                
                if variacion_abs < 0:
                    st.metric("Mejora", f"{abs(variacion_abs):.0f} días menos", border=True, delta=variacion_abs, delta_color="inverse")
                else:
                    st.metric("Empeoramiento", f"{variacion_abs:+.0f} días más", border=True)
        
        # Interpretación
        if total_dias == 0:
            st.success("🌟 ¡Excelente! Sin accidentes laborales en el período.")
        elif promedio_mensual <= 3:
            st.info("✅ Nivel aceptable de seguridad. Mantener las prácticas preventivas.")
        elif promedio_mensual <= 8:
            st.warning("⚠️ Días de baja por encima del objetivo. Revisar protocolos de seguridad.")
        else:
            st.error("🔴 Nivel crítico de accidentabilidad. Se requiere intervención urgente en seguridad e higiene.")
        
        render_info_metrica(8)
    else:
        st.info("No hay datos de accidentes laborales para el período seleccionado")

st.markdown("---")

# ============================================
# COMPOSICIÓN DEL EQUIPO
# ============================================

st.header("👥 Composición del Equipo")

if not df_empleados.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.subheader("Distribución por Área")
            
            # Contar empleados por área
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
            st.subheader("Distribución por Género")
            
            # Contar empleados por género
            genero_counts = df_empleados['genero'].value_counts().reset_index()
            genero_counts.columns = ['genero', 'cantidad']
            
            # Mapear códigos a nombres
            genero_map = {'M': 'Masculino', 'F': 'Femenino'}
            genero_counts['genero'] = genero_counts['genero'].map(genero_map)
            
            fig = px.bar(
                genero_counts,
                x='genero',
                y='cantidad',
                title='Empleados por Género',
                color='genero',
                color_discrete_map={'Masculino': '#1f77b4', 'Femenino': '#ff7f0e'}
            )
            
            fig.update_layout(
                height=300,
                xaxis_title='',
                yaxis_title='Cantidad',
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Métricas del equipo
    st.markdown("#### 📊 Métricas del Equipo")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_empleados = len(df_empleados)
        st.metric("Total Empleados", total_empleados, border=True)
    
    with col2:
        # Diversidad de género
        if 'genero' in df_empleados.columns:
            genero_counts = df_empleados['genero'].value_counts()
            if len(genero_counts) >= 2:
                diversidad = min(genero_counts.values) / max(genero_counts.values) * 100
                st.metric("Índice de Diversidad", f"{diversidad:.0f}%", border=True)
    
    with col3:
        # Antigüedad promedio
        if 'fecha_ingreso' in df_empleados.columns:
            df_empleados['fecha_ingreso'] = pd.to_datetime(df_empleados['fecha_ingreso'])
            antiguedad_promedio = (pd.Timestamp.now() - df_empleados['fecha_ingreso']).dt.days.mean() / 365
            st.metric("Antigüedad Promedio", f"{antiguedad_promedio:.1f} años", border=True)
    
    with col4:
        # Áreas representadas
        num_areas = df_empleados['area'].nunique()
        st.metric("Áreas", num_areas, border=True)

else:
    st.info("No hay información de empleados disponible")

st.markdown("---")

# ============================================
# DATOS DETALLADOS
# ============================================

st.header("📋 Datos Detallados")

with st.expander("Ver tabla de datos completa"):
    df_display = df_filtrado[['fecha', 'metrica', 'valor', 'unidad', 'nombre_area']].copy()
    df_display['fecha'] = df_display['fecha'].dt.strftime('%Y-%m-%d')
    df_display['valor_formateado'] = df_display.apply(
        lambda row: formatear_valor(row['valor'], row['unidad']),
        axis=1
    )
    df_display = df_display.sort_values('fecha', ascending=False)
    
    st.dataframe(
        df_display[['fecha', 'metrica', 'valor_formateado', 'nombre_area']],
        hide_index=True,
        use_container_width=True,
        column_config={
            'fecha': st.column_config.TextColumn('Fecha'),
            'metrica': st.column_config.TextColumn('Métrica'),
            'valor_formateado': st.column_config.TextColumn('Valor'),
            'nombre_area': st.column_config.TextColumn('Área')
        }
    )
    
    # Botón de descarga
    csv = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar datos sociales (CSV)",
        data=csv,
        file_name=f'datos_sociales_{fecha_inicio}_{fecha_fin}.csv',
        mime='text/csv',
    )

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.caption("👥 Análisis Social | Sustainable Growth Monitor")
st.caption(f"📊 Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')} | Registros: {len(df_filtrado):,}")