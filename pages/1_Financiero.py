"""
💰 Página Financiero
Análisis de métricas financieras
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

# Importar utilidades
from utils.database import load_fact_monitoreo, get_date_range, get_metrica_by_id
from utils.config import (
    calcular_estado_metrica, 
    formatear_valor,
    DESCRIPCIONES_METRICAS,
    METRICAS_POR_CATEGORIA
)
from utils.analytics import (
    calcular_variacion,
    agregar_por_mes,
    calcular_margen_operativo
)
from utils.components import (
    render_filtros_sidebar,
    render_kpi_card,
    render_grafico_tendencia,
    render_info_metrica,
    render_resumen_ejecutivo
)

# ============================================
# CONFIGURACIÓN DE PÁGINA
# ============================================

st.set_page_config(
    page_title="Financiero | Sustainable Growth",
    page_icon="💰",
    layout="wide"
)

# ============================================
# HEADER
# ============================================

st.title("💰 Análisis Financiero")
st.markdown("""
Monitoreo integral de métricas económicas: ingresos, costos y gastos operativos.
Visualiza tendencias, identifica oportunidades y optimiza la rentabilidad de tu negocio.
""")

st.markdown("---")

# ============================================
# CARGAR DATOS
# ============================================

# Obtener rango de fechas disponible
try:
    fecha_min, fecha_max = get_date_range()
    
    # Cargar todos los datos
    df_todos = load_fact_monitoreo()
    
    # Aplicar filtros desde sidebar
    fecha_inicio, fecha_fin, _, area_seleccionada = render_filtros_sidebar(
        df_todos,
        mostrar_area=True,
        mostrar_categoria=False  # Ya estamos en Financiero
    )
    
    # Filtrar datos
    df_filtrado = load_fact_monitoreo(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        categoria='Financiera',
        area=area_seleccionada if area_seleccionada != 'Todas' else None
    )
    
    if df_filtrado.empty:
        st.warning("⚠️ No hay datos financieros disponibles para el período seleccionado")
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

st.header("📊 Indicadores Clave")

# Obtener valores del último período y período anterior
fecha_ultimo = df_filtrado['fecha'].max()
fecha_anterior = df_filtrado[df_filtrado['fecha'] < fecha_ultimo]['fecha'].max()

df_ultimo = df_filtrado[df_filtrado['fecha'] == fecha_ultimo]
df_anterior = df_filtrado[df_filtrado['fecha'] == fecha_anterior] if not pd.isna(fecha_anterior) else pd.DataFrame()

# IDs de métricas financieras
ids_financiero = METRICAS_POR_CATEGORIA['Financiera']

# Crear KPI cards
with st.container(horizontal=True):
    for id_metrica in ids_financiero:
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
# EVOLUCIÓN TEMPORAL
# ============================================

st.header("📈 Evolución Temporal")

tab1, tab2, tab3 = st.tabs(["💵 Ingresos", "💸 Costos", "👥 Gastos de Personal"])

with tab1:
    st.subheader("Evolución de Ingresos")
    
    with st.container(border=True):
        # Datos de ingresos (id_metrica = 1)
        df_ingresos = df_filtrado[df_filtrado['id_metrica'] == 1].copy()
        
        if not df_ingresos.empty:
            # Agregar por mes
            df_monthly = df_ingresos.groupby(['anio', 'mes']).agg({
                'valor': 'sum'
            }).reset_index()
            df_monthly['fecha'] = pd.to_datetime(
                                    df_monthly.rename(columns={
                                        'anio': 'year',
                                        'mes': 'month'
                                    })[['year', 'month']].assign(day=1)
                                )
            
            # Gráfico de línea
            fig = px.line(
                df_monthly,
                x='fecha',
                y='valor',
                title='Ingresos Mensuales',
                markers=True
            )
            
            fig.update_layout(
                height=350,
                xaxis_title='',
                yaxis_title='Ingresos (ARS)',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Estadísticas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Período", formatear_valor(df_monthly['valor'].sum(), 'ARS'), border=True)
            
            with col2:
                st.metric("Promedio Mensual", formatear_valor(df_monthly['valor'].mean(), 'ARS'), border=True)
            
            with col3:
                st.metric("Mejor Mes", formatear_valor(df_monthly['valor'].max(), 'ARS'), border=True)
            
            with col4:
                # Calcular tendencia
                if len(df_monthly) >= 2:
                    primer_valor = df_monthly.iloc[0]['valor']
                    ultimo_valor = df_monthly.iloc[-1]['valor']
                    _, crecimiento = calcular_variacion(ultimo_valor, primer_valor)
                    st.metric("Crecimiento", f"{crecimiento:+.1f}%", border=True)
            
            # Información adicional
            render_info_metrica(1)
        else:
            st.info("No hay datos de ingresos para el período seleccionado")

with tab2:
    st.subheader("Evolución de Costos de Compras")
    
    with st.container(border=True):
        # Datos de costos (id_metrica = 2)
        df_costos = df_filtrado[df_filtrado['id_metrica'] == 2].copy()
        
        if not df_costos.empty:
            # Agregar por mes
            df_monthly = df_costos.groupby(['anio', 'mes']).agg({
                'valor': 'sum'
            }).reset_index()
            df_monthly['fecha'] = pd.to_datetime(df_monthly[['anio', 'mes']].assign(day=1))
            
            # Gráfico de barras
            fig = px.bar(
                df_monthly,
                x='fecha',
                y='valor',
                title='Costos de Compras Mensuales',
                color_discrete_sequence=['#ff7f0e']
            )
            
            fig.update_layout(
                height=350,
                xaxis_title='',
                yaxis_title='Costos (ARS)',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Estadísticas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Período", formatear_valor(df_monthly['valor'].sum(), 'ARS'), border=True)
            
            with col2:
                st.metric("Promedio Mensual", formatear_valor(df_monthly['valor'].mean(), 'ARS'), border=True)
            
            with col3:
                st.metric("Mes con Mayor Costo", formatear_valor(df_monthly['valor'].max(), 'ARS'), border=True)
            
            with col4:
                # Variación
                if len(df_monthly) >= 2:
                    primer_valor = df_monthly.iloc[0]['valor']
                    ultimo_valor = df_monthly.iloc[-1]['valor']
                    _, variacion = calcular_variacion(ultimo_valor, primer_valor)
                    delta_label = "Reducción" if variacion < 0 else "Aumento"
                    st.metric(delta_label, f"{abs(variacion):.1f}%", border=True)
            
            render_info_metrica(2)
        else:
            st.info("No hay datos de costos para el período seleccionado")

with tab3:
    st.subheader("Evolución de Gastos de Personal")
    
    with st.container(border=True):
        # Datos de gastos (id_metrica = 3)
        df_gastos = df_filtrado[df_filtrado['id_metrica'] == 3].copy()
        
        if not df_gastos.empty:
            # Agregar por mes
            df_monthly = df_gastos.groupby(['anio', 'mes']).agg({
                'valor': 'sum'
            }).reset_index()
            df_monthly['fecha'] = pd.to_datetime(df_monthly[['anio', 'mes']].assign(day=1))
            
            # Gráfico de área
            fig = px.area(
                df_monthly,
                x='fecha',
                y='valor',
                title='Gastos de Personal Mensuales',
                color_discrete_sequence=['#2ca02c']
            )
            
            fig.update_layout(
                height=350,
                xaxis_title='',
                yaxis_title='Gastos (ARS)',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Estadísticas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Período", formatear_valor(df_monthly['valor'].sum(), 'ARS'), border=True)
            
            with col2:
                st.metric("Promedio Mensual", formatear_valor(df_monthly['valor'].mean(), 'ARS'), border=True)
            
            with col3:
                st.metric("Mes con Mayor Gasto", formatear_valor(df_monthly['valor'].max(), 'ARS'), border=True)
            
            with col4:
                # Variación
                if len(df_monthly) >= 2:
                    primer_valor = df_monthly.iloc[0]['valor']
                    ultimo_valor = df_monthly.iloc[-1]['valor']
                    _, variacion = calcular_variacion(ultimo_valor, primer_valor)
                    delta_label = "Reducción" if variacion < 0 else "Aumento"
                    st.metric(delta_label, f"{abs(variacion):.1f}%", border=True)
            
            render_info_metrica(3)
        else:
            st.info("No hay datos de gastos para el período seleccionado")

st.markdown("---")

# ============================================
# ANÁLISIS COMPARATIVO
# ============================================

st.header("📊 Análisis Comparativo")

with st.container(border=True):
    st.subheader("Evolución de las Tres Métricas Financieras")
    
    # Preparar datos para comparación
    df_comparativo = []
    
    for id_metrica in ids_financiero:
        df_metrica = df_filtrado[df_filtrado['id_metrica'] == id_metrica]
        if not df_metrica.empty:
            df_monthly = df_metrica.groupby(['anio', 'mes', 'metrica']).agg({
                'valor': 'sum'
            }).reset_index()
            df_monthly['fecha'] = pd.to_datetime(df_monthly[['anio', 'mes']].assign(day=1))
            df_comparativo.append(df_monthly)
    
    if df_comparativo:
        df_comp = pd.concat(df_comparativo, ignore_index=True)
        
        fig = px.line(
            df_comp,
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
        
        st.info("💡 **Insight**: Analiza cómo evolucionan tus ingresos en relación con tus costos y gastos para identificar oportunidades de optimización.")

# ============================================
# MARGEN OPERATIVO (MÉTRICA DERIVADA)
# ============================================

st.markdown("---")
st.header("💹 Margen Operativo")

with st.container(border=True):
    st.markdown("""
    **Margen Operativo** = (Ingresos - Costos - Gastos) / Ingresos × 100
    
    Mide la rentabilidad operativa del negocio. Un margen creciente indica mejora en eficiencia.
    """)
    
    # Calcular margen operativo
    try:
        df_ingresos_full = df_filtrado[df_filtrado['id_metrica'] == 1]
        df_costos_full = df_filtrado[df_filtrado['id_metrica'] == 2]
        df_gastos_full = df_filtrado[df_filtrado['id_metrica'] == 3]
        
        if not df_ingresos_full.empty and not df_costos_full.empty and not df_gastos_full.empty:
            df_margen = calcular_margen_operativo(df_ingresos_full, df_costos_full, df_gastos_full)
            
            if not df_margen.empty:
                fig = px.line(
                    df_margen,
                    x='fecha',
                    y='margen_operativo',
                    title='Evolución del Margen Operativo',
                    markers=True,
                    color_discrete_sequence=['#9467bd']
                )
                
                fig.update_layout(
                    height=300,
                    xaxis_title='',
                    yaxis_title='Margen Operativo (%)',
                    hovermode='x unified'
                )
                
                # Añadir línea de referencia en 12% (objetivo típico)
                fig.add_hline(y=12, line_dash="dash", line_color="green", 
                             annotation_text="Objetivo: 12%")
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Métricas del margen
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    margen_actual = df_margen.iloc[-1]['margen_operativo']
                    st.metric("Margen Actual", f"{margen_actual:.1f}%", border=True)
                
                with col2:
                    margen_promedio = df_margen['margen_operativo'].mean()
                    st.metric("Margen Promedio", f"{margen_promedio:.1f}%", border=True)
                
                with col3:
                    margen_mejor = df_margen['margen_operativo'].max()
                    st.metric("Mejor Margen", f"{margen_mejor:.1f}%", border=True)
                
                # Interpretación
                if margen_actual >= 12:
                    st.success("✅ Excelente margen operativo. El negocio es rentable.")
                elif margen_actual >= 5:
                    st.warning("⚠️ Margen operativo aceptable, pero hay espacio para mejorar.")
                else:
                    st.error("🔴 Margen operativo bajo. Se requieren acciones correctivas urgentes.")
    except Exception as e:
        st.warning(f"No se pudo calcular el margen operativo: {e}")

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
        label="📥 Descargar datos financieros (CSV)",
        data=csv,
        file_name=f'datos_financieros_{fecha_inicio}_{fecha_fin}.csv',
        mime='text/csv',
    )

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.caption("💰 Análisis Financiero | Sustainable Growth Monitor")
st.caption(f"📊 Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')} | Registros: {len(df_filtrado):,}")