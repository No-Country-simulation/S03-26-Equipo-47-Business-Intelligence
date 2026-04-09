"""
Componentes visuales reutilizables para el dashboard
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.config import (
    calcular_estado_metrica, 
    formatear_valor,
    obtener_color_categoria,
    obtener_color_estado,
    ALTURA_GRAFICOS
)
from utils.analytics import calcular_variacion

# ============================================
# COMPONENTES DE FILTROS
# ============================================

def render_filtros_sidebar(df_datos, mostrar_area=True, mostrar_categoria=True):
    """
    Renderiza filtros estándar en el sidebar
    
    Args:
        df_datos: DataFrame con los datos
        mostrar_area: Si se debe mostrar filtro de área
        mostrar_categoria: Si se debe mostrar filtro de categoría
    
    Returns:
        tuple: (fecha_inicio, fecha_fin, categoria_seleccionada, area_seleccionada)
    """
    if df_datos.empty:
        st.sidebar.warning("No hay datos disponibles")
        return None, None, None, None
    
    # Filtro de fechas
    st.sidebar.subheader("📅 Período de Análisis")
    
    fecha_min = df_datos['fecha'].min()
    fecha_max = df_datos['fecha'].max()
    
    # Últimos 12 meses por defecto
    from datetime import timedelta
    fecha_inicio_default = max(fecha_min, fecha_max - timedelta(days=365))
    
    fecha_inicio = st.sidebar.date_input(
        "Desde",
        value=fecha_inicio_default,
        min_value=fecha_min,
        max_value=fecha_max
    )
    
    fecha_fin = st.sidebar.date_input(
        "Hasta",
        value=fecha_max,
        min_value=fecha_min,
        max_value=fecha_max
    )
    
    # Filtro de categoría
    categoria_seleccionada = None
    if mostrar_categoria:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🏷️ Categoría ESG")
        categorias = ['Todas'] + sorted(df_datos['categoria'].unique().tolist())
        categoria_seleccionada = st.sidebar.selectbox(
            "Filtrar por categoría",
            categorias,
            label_visibility="collapsed"
        )
    
    # Filtro de área
    area_seleccionada = None
    if mostrar_area:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🏢 Área")
        areas = ['Todas'] + sorted(df_datos['nombre_area'].unique().tolist())
        area_seleccionada = st.sidebar.selectbox(
            "Filtrar por área",
            areas,
            label_visibility="collapsed"
        )
    
    return fecha_inicio, fecha_fin, categoria_seleccionada, area_seleccionada

# ============================================
# KPI CARDS
# ============================================

def render_kpi_card(metrica, valor_actual, unidad, valor_anterior=None, 
                   sparkline_data=None, id_metrica=None):
    """
    Renderiza una tarjeta KPI con métrica
    
    Args:
        metrica: Nombre de la métrica
        valor_actual: Valor actual
        unidad: Unidad de medida
        valor_anterior: Valor del período anterior (opcional)
        sparkline_data: Lista de valores para sparkline (opcional)
        id_metrica: ID de métrica para calcular estado (opcional)
    """
    # Calcular delta
    if valor_anterior is not None:
        _, delta_pct = calcular_variacion(valor_actual, valor_anterior)
        delta_str = f"{delta_pct:+.1f}%"
    else:
        delta_str = None
    
    # Estado de la métrica
    if id_metrica is not None:
        estado_emoji, _ = calcular_estado_metrica(id_metrica, valor_actual)
        label = f"{estado_emoji} {metrica}"
    else:
        label = metrica
    
    # Formatear valor
    valor_display = formatear_valor(valor_actual, unidad)
    
    # Renderizar
    st.metric(
        label,
        valor_display,
        delta_str,
        border=True,
        chart_data=sparkline_data if sparkline_data and len(sparkline_data) > 1 else None,
        chart_type="line"
    )

# ============================================
# GRÁFICOS DE TENDENCIAS
# ============================================

def render_grafico_tendencia(df, titulo, altura=None):
    """
    Renderiza un gráfico de líneas de tendencia
    
    Args:
        df: DataFrame con columnas 'fecha', 'valor', 'metrica'
        titulo: Título del gráfico
        altura: Altura del gráfico (opcional)
    """
    if df.empty:
        st.info("No hay datos para mostrar")
        return
    
    altura = altura or ALTURA_GRAFICOS['tendencia']
    
    # Crear gráfico
    fig = px.line(
        df,
        x='fecha',
        y='valor',
        color='metrica' if 'metrica' in df.columns else None,
        title=titulo,
        markers=True
    )
    
    fig.update_layout(
        height=altura,
        hovermode='x unified',
        xaxis_title='',
        yaxis_title='Valor',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_grafico_barras(df, x, y, titulo, color=None, altura=None):
    """
    Renderiza un gráfico de barras
    
    Args:
        df: DataFrame con los datos
        x: Columna para eje X
        y: Columna para eje Y
        titulo: Título del gráfico
        color: Columna para color (opcional)
        altura: Altura del gráfico (opcional)
    """
    if df.empty:
        st.info("No hay datos para mostrar")
        return
    
    altura = altura or ALTURA_GRAFICOS['tendencia']
    
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        title=titulo
    )
    
    fig.update_layout(
        height=altura,
        xaxis_title='',
        yaxis_title='Valor'
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ============================================
# GRÁFICOS DE CORRELACIÓN
# ============================================

def render_grafico_correlacion(df, x, y, x_label, y_label, titulo, 
                               mostrar_tendencia=True, altura=None):
    """
    Renderiza un gráfico de dispersión con línea de tendencia
    
    Args:
        df: DataFrame con los datos
        x: Columna para eje X
        y: Columna para eje Y
        x_label: Etiqueta eje X
        y_label: Etiqueta eje Y
        titulo: Título del gráfico
        mostrar_tendencia: Si mostrar línea de tendencia
        altura: Altura del gráfico (opcional)
    """
    if df.empty or len(df) < 2:
        st.info("No hay suficientes datos para calcular correlación")
        return
    
    altura = altura or ALTURA_GRAFICOS['correlacion']
    
    fig = px.scatter(
        df,
        x=x,
        y=y,
        trendline='ols' if mostrar_tendencia else None,
        labels={x: x_label, y: y_label},
        title=titulo
    )
    
    fig.update_layout(height=altura)
    
    st.plotly_chart(fig, use_container_width=True)

# ============================================
# GRÁFICOS COMPARATIVOS
# ============================================

def render_grafico_comparativo_categorias(df_resumen, titulo="Estado por Categoría"):
    """
    Renderiza gráfico de barras apiladas comparando estados por categoría
    
    Args:
        df_resumen: DataFrame con columnas ['Categoría', '🔴 Críticas', '🟡 Precaución', '🟢 Óptimas']
        titulo: Título del gráfico
    """
    if df_resumen.empty:
        st.info("No hay datos para mostrar")
        return
    
    # Preparar datos para gráfico
    df_plot = df_resumen.melt(
        id_vars=['Categoría'],
        value_vars=['🔴 Críticas', '🟡 Precaución', '🟢 Óptimas'],
        var_name='Estado',
        value_name='Cantidad'
    )
    
    fig = px.bar(
        df_plot,
        x='Categoría',
        y='Cantidad',
        color='Estado',
        title=titulo,
        barmode='stack',
        color_discrete_map={
            '🔴 Críticas': '#d62728',
            '🟡 Precaución': '#ff7f0e',
            '🟢 Óptimas': '#2ca02c'
        }
    )
    
    fig.update_layout(height=ALTURA_GRAFICOS['comparativa'])
    
    st.plotly_chart(fig, use_container_width=True)

# ============================================
# TABLAS DE DATOS
# ============================================

def render_tabla_metricas(df, mostrar_estado=True):
    """
    Renderiza una tabla con métricas y sus valores
    
    Args:
        df: DataFrame con columnas ['metrica', 'valor', 'unidad', 'id_metrica']
        mostrar_estado: Si mostrar columna de estado
    """
    if df.empty:
        st.info("No hay métricas para mostrar")
        return
    
    # Preparar datos
    df_display = df.copy()
    
    if mostrar_estado and 'id_metrica' in df.columns:
        df_display['estado'] = df_display.apply(
            lambda row: calcular_estado_metrica(row['id_metrica'], row['valor'])[0],
            axis=1
        )
    
    # Formatear valores
    df_display['valor_formateado'] = df_display.apply(
        lambda row: formatear_valor(row['valor'], row['unidad']),
        axis=1
    )
    
    # Seleccionar columnas a mostrar
    columnas = ['metrica', 'valor_formateado']
    if mostrar_estado:
        columnas.insert(0, 'estado')
    
    st.dataframe(
        df_display[columnas],
        hide_index=True,
        use_container_width=True,
        column_config={
            'estado': st.column_config.TextColumn('Estado', width='small'),
            'metrica': st.column_config.TextColumn('Métrica'),
            'valor_formateado': st.column_config.TextColumn('Valor')
        }
    )

# ============================================
# ALERTAS Y NOTIFICACIONES
# ============================================

def render_alerta(tipo, titulo, mensaje):
    """
    Renderiza una alerta con formato
    
    Args:
        tipo: 'error', 'warning', 'success', 'info'
        titulo: Título de la alerta
        mensaje: Mensaje detallado
    """
    with st.container(border=True):
        col1, col2 = st.columns([1, 10])
        
        with col1:
            if tipo == 'error':
                st.markdown("# 🔴")
            elif tipo == 'warning':
                st.markdown("# 🟡")
            elif tipo == 'success':
                st.markdown("# 🟢")
            else:
                st.markdown("# 🔵")
        
        with col2:
            st.markdown(f"**{titulo}**")
            st.markdown(mensaje)

# ============================================
# RESUMEN EJECUTIVO
# ============================================

def render_resumen_ejecutivo(df_metricas, periodo):
    """
    Renderiza un resumen ejecutivo con métricas clave
    
    Args:
        df_metricas: DataFrame con métricas del período
        periodo: String describiendo el período
    """
    st.markdown(f"### 📊 Resumen Ejecutivo - {periodo}")
    
    with st.container(border=True):
        # Contar estados
        estados_count = {
            'critical': 0,
            'warning': 0,
            'optimal': 0
        }
        
        for _, row in df_metricas.iterrows():
            if 'id_metrica' in row:
                _, estado = calcular_estado_metrica(row['id_metrica'], row['valor'])
                if estado in estados_count:
                    estados_count[estado] += 1
        
        # Mostrar resumen
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "🔴 Métricas Críticas",
                estados_count['critical'],
                border=True
            )
        
        with col2:
            st.metric(
                "🟡 En Precaución",
                estados_count['warning'],
                border=True
            )
        
        with col3:
            st.metric(
                "🟢 Óptimas",
                estados_count['optimal'],
                border=True
            )
        
        # Mensaje general
        if estados_count['critical'] > 0:
            st.error(f"⚠️ Hay {estados_count['critical']} métrica(s) crítica(s) que requieren atención inmediata")
        elif estados_count['warning'] > 0:
            st.warning(f"⚠️ Hay {estados_count['warning']} métrica(s) en estado de precaución")
        else:
            st.success("✅ Todas las métricas están en rangos óptimos")

# ============================================
# INFORMACIÓN CONTEXTUAL
# ============================================

def render_info_metrica(id_metrica):
    """
    Renderiza información contextual sobre una métrica
    
    Args:
        id_metrica: ID de la métrica
    """
    from utils.config import DESCRIPCIONES_METRICAS
    
    if id_metrica not in DESCRIPCIONES_METRICAS:
        return
    
    info = DESCRIPCIONES_METRICAS[id_metrica]
    
    with st.expander("ℹ️ Información de la Métrica"):
        st.markdown(f"**{info['titulo']}**")
        st.markdown(info['descripcion'])
        st.markdown(f"**🎯 Objetivo:** {info['objetivo']}")
        
        if 'acciones_mejora' in info:
            st.markdown("**💡 Acciones de Mejora:**")
            for accion in info['acciones_mejora']:
                st.markdown(f"- {accion}")