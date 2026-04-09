"""
🌍 Página Ambiental
Análisis de métricas ambientales (E)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta

# Importar utilidades
from utils.database import load_fact_monitoreo, get_date_range
from utils.config import (
    calcular_estado_metrica, 
    formatear_valor,
    DESCRIPCIONES_METRICAS,
    METRICAS_POR_CATEGORIA
)
from utils.analytics import (
    calcular_variacion,
    calcular_intensidad_energetica
)
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
    page_title="Ambiental | Sustainable Growth",
    page_icon="🌍",
    layout="wide"
)

# ============================================
# HEADER
# ============================================

st.title("🌍 Análisis Ambiental (E)")
st.markdown("""
Monitoreo de impacto ecológico: consumo energético, gestión de residuos y eficiencia ambiental.
Mide tu huella de carbono y avanza hacia operaciones más sostenibles.
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
    
    # Filtrar datos ambientales
    df_filtrado = load_fact_monitoreo(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        categoria='E',
        area=area_seleccionada if area_seleccionada != 'Todas' else None
    )
    
    if df_filtrado.empty:
        st.warning("⚠️ No hay datos ambientales disponibles para el período seleccionado")
        st.stop()

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

st.header("📊 Indicadores Ambientales Clave")

# Obtener valores del último período y período anterior
fecha_ultimo = df_filtrado['fecha'].max()
fecha_anterior = df_filtrado[df_filtrado['fecha'] < fecha_ultimo]['fecha'].max()

df_ultimo = df_filtrado[df_filtrado['fecha'] == fecha_ultimo]
df_anterior = df_filtrado[df_filtrado['fecha'] == fecha_anterior] if not pd.isna(fecha_anterior) else pd.DataFrame()

# IDs de métricas ambientales
ids_ambiental = METRICAS_POR_CATEGORIA['E']

# Crear KPI cards
with st.container(horizontal=True):
    for id_metrica in ids_ambiental:
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
# CONSUMO ENERGÉTICO
# ============================================

st.header("⚡ Consumo Energético")

tab1, tab2 = st.tabs(["📈 Evolución Temporal", "🎯 Análisis de Eficiencia"])

with tab1:
    with st.container(border=True):
        st.subheader("Evolución del Consumo Energético")
        
        # Datos de energía (id_metrica = 4)
        df_energia = df_filtrado[df_filtrado['id_metrica'] == 4].copy()
        
        if not df_energia.empty:
            # Agregar por mes
            df_monthly = df_energia.groupby(['anio', 'mes']).agg({
                'valor': 'sum'
            }).reset_index()
            df_monthly['fecha'] = pd.to_datetime(df_monthly[['anio', 'mes']].assign(day=1))
            
            # Gráfico de área con objetivo
            fig = go.Figure()
            
            # Área de consumo real
            fig.add_trace(go.Scatter(
                x=df_monthly['fecha'],
                y=df_monthly['valor'],
                mode='lines',
                fill='tozeroy',
                name='Consumo Real',
                line=dict(color='#2ca02c', width=2)
            ))
            
            # Línea de objetivo (120,000 kWh - umbral de precaución)
            fig.add_hline(
                y=120000,
                line_dash="dash",
                line_color="orange",
                annotation_text="Objetivo: 120,000 kWh",
                annotation_position="right"
            )
            
            # Línea crítica (150,000 kWh)
            fig.add_hline(
                y=150000,
                line_dash="dash",
                line_color="red",
                annotation_text="Límite Crítico",
                annotation_position="right"
            )
            
            fig.update_layout(
                title='Consumo Energético Mensual',
                height=350,
                xaxis_title='',
                yaxis_title='Consumo (kWh)',
                hovermode='x unified',
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Estadísticas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Período", formatear_valor(df_monthly['valor'].sum(), 'kWh'), border=True)
            
            with col2:
                st.metric("Promedio Mensual", formatear_valor(df_monthly['valor'].mean(), 'kWh'), border=True)
            
            with col3:
                st.metric("Pico de Consumo", formatear_valor(df_monthly['valor'].max(), 'kWh'), border=True)
            
            with col4:
                # Variación
                if len(df_monthly) >= 2:
                    primer_valor = df_monthly.iloc[0]['valor']
                    ultimo_valor = df_monthly.iloc[-1]['valor']
                    _, variacion = calcular_variacion(ultimo_valor, primer_valor)
                    delta_label = "Reducción" if variacion < 0 else "Aumento"
                    st.metric(delta_label, f"{abs(variacion):.1f}%", border=True)
            
            render_info_metrica(4)
        else:
            st.info("No hay datos de consumo energético para el período seleccionado")

with tab2:
    with st.container(border=True):
        st.subheader("Intensidad Energética")
        st.caption("kWh consumidos por cada peso de ingreso generado")
        
        # Necesitamos datos de energía e ingresos
        df_energia_full = load_fact_monitoreo(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            categoria='E'
        )
        df_energia_full = df_energia_full[df_energia_full['id_metrica'] == 4]
        
        df_ingresos_full = load_fact_monitoreo(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            categoria='Financiera'
        )
        df_ingresos_full = df_ingresos_full[df_ingresos_full['id_metrica'] == 1]
        
        if not df_energia_full.empty and not df_ingresos_full.empty:
            try:
                df_intensidad = calcular_intensidad_energetica(df_energia_full, df_ingresos_full)
                
                if not df_intensidad.empty:
                    fig = px.line(
                        df_intensidad,
                        x='fecha',
                        y='intensidad_energetica',
                        title='Intensidad Energética (kWh/ARS)',
                        markers=True,
                        color_discrete_sequence=['#17becf']
                    )
                    
                    fig.update_layout(
                        height=300,
                        xaxis_title='',
                        yaxis_title='kWh por ARS',
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Interpretación
                    intensidad_actual = df_intensidad.iloc[-1]['intensidad_energetica']
                    intensidad_promedio = df_intensidad['intensidad_energetica'].mean()
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Intensidad Actual", f"{intensidad_actual:.6f} kWh/ARS", border=True)
                    
                    with col2:
                        st.metric("Promedio del Período", f"{intensidad_promedio:.6f} kWh/ARS", border=True)
                    
                    if intensidad_actual < intensidad_promedio:
                        st.success("✅ La eficiencia energética ha mejorado respecto al promedio del período")
                    else:
                        st.warning("⚠️ La intensidad energética está por encima del promedio. Considera acciones de eficiencia.")
            except Exception as e:
                st.warning(f"No se pudo calcular la intensidad energética: {e}")
        else:
            st.info("Se requieren datos de energía e ingresos para calcular la intensidad energética")

st.markdown("---")

# ============================================
# GESTIÓN DE RESIDUOS
# ============================================

st.header("♻️ Gestión de Residuos")

with st.container(border=True):
    st.subheader("Tasa de Reciclaje")
    
    # Datos de reciclaje (id_metrica = 5)
    df_reciclaje = df_filtrado[df_filtrado['id_metrica'] == 5].copy()
    
    if not df_reciclaje.empty:
        # Agregar por mes
        df_monthly = df_reciclaje.groupby(['anio', 'mes']).agg({
            'valor': 'mean'  # Promedio de la tasa
        }).reset_index()
        df_monthly['fecha'] = pd.to_datetime(df_monthly[['anio', 'mes']].assign(day=1))
        
        # Gráfico combinado: línea + barras
        fig = go.Figure()
        
        # Barras de tasa de reciclaje
        fig.add_trace(go.Bar(
            x=df_monthly['fecha'],
            y=df_monthly['valor'],
            name='Tasa de Reciclaje',
            marker_color='#2ca02c',
            opacity=0.7
        ))
        
        # Línea de tendencia
        fig.add_trace(go.Scatter(
            x=df_monthly['fecha'],
            y=df_monthly['valor'],
            mode='lines+markers',
            name='Tendencia',
            line=dict(color='#d62728', width=2),
            marker=dict(size=8)
        ))
        
        # Líneas de referencia
        fig.add_hline(y=80, line_dash="dash", line_color="green", 
                     annotation_text="Excelente: 80%")
        fig.add_hline(y=60, line_dash="dash", line_color="orange",
                     annotation_text="Aceptable: 60%")
        fig.add_hline(y=30, line_dash="dash", line_color="red",
                     annotation_text="Crítico: 30%")
        
        fig.update_layout(
            title='Evolución de la Tasa de Reciclaje',
            height=350,
            xaxis_title='',
            yaxis_title='Tasa de Reciclaje (%)',
            hovermode='x unified',
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Estadísticas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            tasa_actual = df_monthly.iloc[-1]['valor']
            st.metric("Tasa Actual", f"{tasa_actual:.1f}%", border=True)
        
        with col2:
            tasa_promedio = df_monthly['valor'].mean()
            st.metric("Promedio del Período", f"{tasa_promedio:.1f}%", border=True)
        
        with col3:
            mejor_tasa = df_monthly['valor'].max()
            st.metric("Mejor Tasa Alcanzada", f"{mejor_tasa:.1f}%", border=True)
        
        with col4:
            # Variación
            if len(df_monthly) >= 2:
                primer_valor = df_monthly.iloc[0]['valor']
                ultimo_valor = df_monthly.iloc[-1]['valor']
                variacion_abs, _ = calcular_variacion(ultimo_valor, primer_valor)
                st.metric("Mejora", f"{variacion_abs:+.1f} pts", border=True)
        
        # Interpretación
        if tasa_actual >= 80:
            st.success("🌟 ¡Excelente! La tasa de reciclaje está en niveles óptimos")
        elif tasa_actual >= 60:
            st.info("👍 Buen nivel de reciclaje, pero hay margen para mejorar")
        elif tasa_actual >= 30:
            st.warning("⚠️ Tasa de reciclaje por debajo del objetivo. Se requieren acciones correctivas")
        else:
            st.error("🔴 Tasa de reciclaje crítica. Implementar programa de gestión de residuos urgente")
        
        render_info_metrica(5)
    else:
        st.info("No hay datos de reciclaje para el período seleccionado")

st.markdown("---")

# ============================================
# OBJETIVOS AMBIENTALES
# ============================================

st.header("🎯 Progreso hacia Objetivos Ambientales")

with st.container(border=True):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚡ Reducción Energética")
        st.markdown("**Objetivo:** -8% anual")
        
        # Calcular reducción anual
        df_energia = df_filtrado[df_filtrado['id_metrica'] == 4]
        
        if not df_energia.empty and len(df_energia['anio'].unique()) >= 2:
            # Comparar años
            anios = sorted(df_energia['anio'].unique())
            
            if len(anios) >= 2:
                anio_anterior = anios[-2]
                anio_actual = anios[-1]
                
                consumo_anterior = df_energia[df_energia['anio'] == anio_anterior]['valor'].sum()
                consumo_actual = df_energia[df_energia['anio'] == anio_actual]['valor'].sum()
                
                _, reduccion_pct = calcular_variacion(consumo_actual, consumo_anterior)
                
                # Barra de progreso
                progreso = min(abs(reduccion_pct) / 8 * 100, 100) if reduccion_pct < 0 else 0
                
                st.progress(progreso / 100)
                st.metric("Reducción Lograda", f"{reduccion_pct:.1f}%", border=True)
                
                if reduccion_pct <= -8:
                    st.success("✅ ¡Objetivo alcanzado!")
                elif reduccion_pct < 0:
                    st.info(f"📊 Progreso: {progreso:.0f}% del objetivo")
                else:
                    st.error("🔴 Consumo aumentó en lugar de reducirse")
        else:
            st.info("Se requieren datos de al menos 2 años para calcular")
    
    with col2:
        st.markdown("### ♻️ Meta de Reciclaje")
        st.markdown("**Objetivo:** >60% de residuos reciclados")
        
        # Tasa actual
        df_reciclaje = df_filtrado[df_filtrado['id_metrica'] == 5]
        
        if not df_reciclaje.empty:
            tasa_actual = df_reciclaje['valor'].iloc[-1]
            
            # Barra de progreso
            progreso = min(tasa_actual / 60 * 100, 100)
            
            st.progress(progreso / 100)
            st.metric("Tasa Actual", f"{tasa_actual:.1f}%", border=True)
            
            if tasa_actual >= 60:
                st.success("✅ ¡Objetivo alcanzado!")
            else:
                falta = 60 - tasa_actual
                st.warning(f"⚠️ Faltan {falta:.1f} puntos para alcanzar el objetivo")
        else:
            st.info("No hay datos de reciclaje disponibles")

st.markdown("---")

# ============================================
# COMPARATIVA TEMPORAL
# ============================================

st.header("📊 Comparativa Interanual")

with st.container(border=True):
    st.subheader("Evolución de Métricas Ambientales por Año")
    
    # Agrupar por año
    df_anual = df_filtrado.groupby(['anio', 'metrica']).agg({
        'valor': 'mean'  # Promedio anual
    }).reset_index()
    
    if not df_anual.empty:
        fig = px.bar(
            df_anual,
            x='anio',
            y='valor',
            color='metrica',
            title='Comparación Anual de Métricas Ambientales',
            barmode='group',
            color_discrete_sequence=['#2ca02c', '#17becf']
        )
        
        fig.update_layout(
            height=350,
            xaxis_title='Año',
            yaxis_title='Valor Promedio',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("💡 **Insight**: Identifica tendencias de largo plazo en tus métricas ambientales para evaluar el impacto de tus iniciativas verdes.")

# ============================================
# DATOS DETALLADOS
# ============================================

st.markdown("---")
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
        label="📥 Descargar datos ambientales (CSV)",
        data=csv,
        file_name=f'datos_ambientales_{fecha_inicio}_{fecha_fin}.csv',
        mime='text/csv',
    )

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.caption("🌍 Análisis Ambiental | Sustainable Growth Monitor")
st.caption(f"📊 Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')} | Registros: {len(df_filtrado):,}")