"""
⚠️ Página Alertas
Sistema de alertas y recomendaciones automáticas
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Importar utilidades
from utils.database import load_fact_monitoreo, get_date_range, load_dim_metrica
from utils.config import (
    calcular_estado_metrica,
    obtener_recomendacion,
    formatear_valor,
    UMBRALES,
    DESCRIPCIONES_METRICAS
)
from utils.analytics import calcular_variacion, detectar_anomalias
from utils.components import render_filtros_sidebar, render_alerta

# ============================================
# CONFIGURACIÓN DE PÁGINA
# ============================================

st.set_page_config(
    page_title="Alertas | Sustainable Growth",
    page_icon="⚠️",
    layout="wide"
)

# ============================================
# HEADER
# ============================================

st.title("⚠️ Sistema de Alertas y Recomendaciones")
st.markdown("""
Monitoreo proactivo de métricas críticas. Detecta desviaciones, anomalías y recibe
recomendaciones automáticas para mantener tu negocio en el camino correcto.
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
    fecha_inicio, fecha_fin, categoria_seleccionada, area_seleccionada = render_filtros_sidebar(
        df_todos,
        mostrar_area=True,
        mostrar_categoria=True
    )
    
    # Filtrar datos
    df_filtrado = load_fact_monitoreo(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        categoria=categoria_seleccionada if categoria_seleccionada != 'Todas' else None,
        area=area_seleccionada if area_seleccionada != 'Todas' else None
    )
    
    if df_filtrado.empty:
        st.warning("⚠️ No hay datos disponibles para el período seleccionado")
        st.stop()
    
    # Cargar catálogo de métricas
    df_metricas = load_dim_metrica()

except Exception as e:
    st.error(f"❌ Error al cargar datos: {e}")
    st.info("💡 Verifica que la base de datos esté configurada correctamente")
    st.stop()

# ============================================
# ESTADO GENERAL
# ============================================

st.header("📊 Estado General del Sistema")

# Obtener último período
fecha_ultimo = df_filtrado['fecha'].max()
df_ultimo = df_filtrado[df_filtrado['fecha'] == fecha_ultimo]

# Calcular estados
estados = {
    'critical': [],
    'warning': [],
    'optimal': []
}

for _, row in df_ultimo.iterrows():
    if row['id_metrica'] in UMBRALES:
        _, estado = calcular_estado_metrica(row['id_metrica'], row['valor'])
        estados[estado].append({
            'metrica': row['metrica'],
            'valor': row['valor'],
            'unidad': row['unidad'],
            'id_metrica': row['id_metrica'],
            'area': row['nombre_area']
        })

# Tarjetas de resumen
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("### 🔴 Críticas")
        st.markdown(f"<h1 style='text-align: center; color: #d62728;'>{len(estados['critical'])}</h1>", 
                   unsafe_allow_html=True)
        st.markdown("Requieren acción inmediata")

with col2:
    with st.container(border=True):
        st.markdown("### 🟡 Precaución")
        st.markdown(f"<h1 style='text-align: center; color: #ff7f0e;'>{len(estados['warning'])}</h1>",
                   unsafe_allow_html=True)
        st.markdown("Monitorear de cerca")

with col3:
    with st.container(border=True):
        st.markdown("### 🟢 Óptimas")
        st.markdown(f"<h1 style='text-align: center; color: #2ca02c;'>{len(estados['optimal'])}</h1>",
                   unsafe_allow_html=True)
        st.markdown("Dentro de objetivos")

st.markdown("---")

# ============================================
# ALERTAS CRÍTICAS
# ============================================

if len(estados['critical']) > 0:
    st.header("🔴 Alertas Críticas - Acción Inmediata Requerida")
    
    for alerta in estados['critical']:
        with st.container(border=True):
            col1, col2, col3 = st.columns([2, 2, 4])
            
            with col1:
                st.markdown(f"### 🔴 {alerta['metrica']}")
                st.caption(f"Área: {alerta['area']}")
            
            with col2:
                valor_formateado = formatear_valor(alerta['valor'], alerta['unidad'])
                st.markdown(f"#### {valor_formateado}")
                
                # Mostrar umbral
                if alerta['id_metrica'] in UMBRALES:
                    umbral = UMBRALES[alerta['id_metrica']]
                    if umbral.get('tipo') == 'menor_mejor':
                        st.caption(f"Límite: {formatear_valor(umbral['critico'], alerta['unidad'])}")
                    else:
                        st.caption(f"Mínimo: {formatear_valor(umbral['critico'], alerta['unidad'])}")
            
            with col3:
                # Obtener recomendación
                recomendacion = obtener_recomendacion(alerta['id_metrica'], 'critical')
                
                if recomendacion:
                    st.markdown(recomendacion)
                else:
                    st.markdown("**Acción requerida:** Revisar esta métrica inmediatamente y tomar medidas correctivas.")
                
                # Botón para más info
                if st.button(f"Ver detalles 📊", key=f"critico_{alerta['id_metrica']}"):
                    st.session_state[f"show_detail_{alerta['id_metrica']}"] = True
            
            # Mostrar detalles si se solicitó
            if st.session_state.get(f"show_detail_{alerta['id_metrica']}", False):
                if alerta['id_metrica'] in DESCRIPCIONES_METRICAS:
                    info = DESCRIPCIONES_METRICAS[alerta['id_metrica']]
                    
                    st.markdown("---")
                    st.markdown("#### 📋 Información Detallada")
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.markdown(f"**Descripción:** {info['descripcion']}")
                        st.markdown(f"**Objetivo:** {info['objetivo']}")
                    
                    with col_b:
                        if 'acciones_mejora' in info:
                            st.markdown("**Acciones de Mejora:**")
                            for accion in info['acciones_mejora']:
                                st.markdown(f"- {accion}")

st.markdown("---")

# ============================================
# ALERTAS DE PRECAUCIÓN
# ============================================

if len(estados['warning']) > 0:
    st.header("🟡 Alertas de Precaución - Monitoreo Requerido")
    
    with st.expander(f"Ver {len(estados['warning'])} alerta(s) de precaución", expanded=True):
        for alerta in estados['warning']:
            col1, col2, col3 = st.columns([2, 1, 3])
            
            with col1:
                st.markdown(f"**🟡 {alerta['metrica']}**")
                st.caption(f"Área: {alerta['area']}")
            
            with col2:
                st.markdown(formatear_valor(alerta['valor'], alerta['unidad']))
            
            with col3:
                # Obtener recomendación
                recomendacion = obtener_recomendacion(alerta['id_metrica'], 'warning')
                
                if recomendacion:
                    st.caption(recomendacion)
                else:
                    st.caption("Monitorear evolución y considerar acciones preventivas.")
            
            st.markdown("---")

st.markdown("---")

# ============================================
# MÉTRICAS ÓPTIMAS
# ============================================

with st.expander(f"✅ Ver {len(estados['optimal'])} métrica(s) en estado óptimo"):
    if len(estados['optimal']) > 0:
        df_optimal = pd.DataFrame(estados['optimal'])
        df_optimal['valor_formateado'] = df_optimal.apply(
            lambda row: formatear_valor(row['valor'], row['unidad']),
            axis=1
        )
        
        st.dataframe(
            df_optimal[['metrica', 'valor_formateado', 'area']],
            hide_index=True,
            use_container_width=True,
            column_config={
                'metrica': st.column_config.TextColumn('Métrica'),
                'valor_formateado': st.column_config.TextColumn('Valor'),
                'area': st.column_config.TextColumn('Área')
            }
        )
    else:
        st.info("No hay métricas en estado óptimo en este momento")

st.markdown("---")

# ============================================
# TENDENCIAS PREOCUPANTES
# ============================================

st.header("📉 Tendencias Preocupantes")

st.markdown("""
Métricas que aunque no estén en estado crítico, muestran tendencias negativas
que podrían convertirse en problemas si no se atienden.
""")

with st.container(border=True):
    tendencias_negativas = []
    
    for id_metrica in df_filtrado['id_metrica'].unique():
        if id_metrica in UMBRALES:
            df_metrica = df_filtrado[df_filtrado['id_metrica'] == id_metrica].sort_values('fecha')
            
            if len(df_metrica) >= 4:
                # Obtener últimos 4 valores
                ultimos_valores = df_metrica['valor'].tail(4).tolist()
                
                # Determinar si es métrica de "menor es mejor"
                tipo = UMBRALES[id_metrica].get('tipo', 'mayor_mejor')
                
                # Calcular tendencia
                if tipo == 'menor_mejor':
                    # Para métricas donde menor es mejor, tendencia positiva es MALA
                    if ultimos_valores[-1] > ultimos_valores[0]:
                        # Está aumentando (malo)
                        variacion = ((ultimos_valores[-1] - ultimos_valores[0]) / ultimos_valores[0]) * 100
                        if variacion > 10:  # Aumento de más del 10%
                            tendencias_negativas.append({
                                'metrica': df_metrica['metrica'].iloc[0],
                                'valor_actual': ultimos_valores[-1],
                                'valor_anterior': ultimos_valores[0],
                                'variacion': variacion,
                                'unidad': df_metrica['unidad'].iloc[0],
                                'tipo': 'Aumento indeseado'
                            })
                else:
                    # Para métricas donde mayor es mejor, tendencia negativa es MALA
                    if ultimos_valores[-1] < ultimos_valores[0]:
                        # Está disminuyendo (malo)
                        variacion = ((ultimos_valores[-1] - ultimos_valores[0]) / ultimos_valores[0]) * 100
                        if variacion < -10:  # Disminución de más del 10%
                            tendencias_negativas.append({
                                'metrica': df_metrica['metrica'].iloc[0],
                                'valor_actual': ultimos_valores[-1],
                                'valor_anterior': ultimos_valores[0],
                                'variacion': variacion,
                                'unidad': df_metrica['unidad'].iloc[0],
                                'tipo': 'Disminución indeseada'
                            })
    
    if tendencias_negativas:
        for tendencia in tendencias_negativas:
            render_alerta(
                'warning',
                f"Tendencia negativa: {tendencia['metrica']}",
                f"""
                - Valor actual: {formatear_valor(tendencia['valor_actual'], tendencia['unidad'])}
                - Variación: {tendencia['variacion']:+.1f}%
                - **Recomendación:** Investigar causas y tomar acciones preventivas antes de que se convierta en problema crítico.
                """
            )
    else:
        st.success("✅ No se detectaron tendencias preocupantes en las métricas monitoreadas")

st.markdown("---")

# ============================================
# ANOMALÍAS DETECTADAS
# ============================================

st.header("🔍 Detección de Anomalías")

st.markdown("""
Valores atípicos que se desvían significativamente del patrón histórico,
incluso si están dentro de los umbrales normales.
""")

with st.container(border=True):
    anomalias_encontradas = []
    
    for id_metrica in df_filtrado['id_metrica'].unique():
        df_metrica = df_filtrado[df_filtrado['id_metrica'] == id_metrica].sort_values('fecha')
        
        if len(df_metrica) >= 6:  # Necesitamos suficientes datos
            valores = df_metrica['valor'].values
            anomalias = detectar_anomalias(valores, umbral_desviaciones=2)
            
            if anomalias.any():
                # Obtener los valores anómalos más recientes
                indices_anomalos = [i for i, es_anomalo in enumerate(anomalias) if es_anomalo]
                
                if indices_anomalos:
                    # Tomar el más reciente
                    idx_mas_reciente = indices_anomalos[-1]
                    
                    anomalias_encontradas.append({
                        'metrica': df_metrica['metrica'].iloc[idx_mas_reciente],
                        'fecha': df_metrica['fecha'].iloc[idx_mas_reciente],
                        'valor': df_metrica['valor'].iloc[idx_mas_reciente],
                        'unidad': df_metrica['unidad'].iloc[idx_mas_reciente],
                        'promedio': valores.mean(),
                        'desviacion': valores.std()
                    })
    
    if anomalias_encontradas:
        for anomalia in anomalias_encontradas:
            desviacion_pct = ((anomalia['valor'] - anomalia['promedio']) / anomalia['promedio']) * 100
            
            st.warning(f"""
            **⚠️ Anomalía detectada: {anomalia['metrica']}**
            
            - Fecha: {anomalia['fecha'].strftime('%d/%m/%Y')}
            - Valor: {formatear_valor(anomalia['valor'], anomalia['unidad'])}
            - Promedio histórico: {formatear_valor(anomalia['promedio'], anomalia['unidad'])}
            - Desviación: {desviacion_pct:+.1f}%
            
            **Acción sugerida:** Verificar si este valor es un error de medición o refleja un evento real que requiere atención.
            """)
    else:
        st.success("✅ No se detectaron anomalías estadísticas en el período analizado")

st.markdown("---")

# ============================================
# RESUMEN DE ACCIONES RECOMENDADAS
# ============================================

st.header("📋 Resumen de Acciones Recomendadas")

with st.container(border=True):
    st.markdown("### Plan de Acción Priorizado")
    
    if len(estados['critical']) > 0:
        st.markdown("#### 🔴 Prioridad Alta (Inmediato)")
        for i, alerta in enumerate(estados['critical'], 1):
            recomendacion = obtener_recomendacion(alerta['id_metrica'], 'critical')
            if recomendacion:
                st.markdown(f"{i}. {recomendacion}")
    
    if len(estados['warning']) > 0:
        st.markdown("#### 🟡 Prioridad Media (Esta semana)")
        for i, alerta in enumerate(estados['warning'], 1):
            recomendacion = obtener_recomendacion(alerta['id_metrica'], 'warning')
            if recomendacion:
                st.markdown(f"{i}. {recomendacion}")
    
    if tendencias_negativas:
        st.markdown("#### 📉 Prioridad Baja (Preventivo)")
        for i, tendencia in enumerate(tendencias_negativas, 1):
            st.markdown(f"{i}. Investigar causas de tendencia negativa en **{tendencia['metrica']}**")
    
    if len(estados['critical']) == 0 and len(estados['warning']) == 0 and not tendencias_negativas:
        st.success("✅ No hay acciones críticas pendientes. ¡Mantén el buen trabajo!")

st.markdown("---")

# ============================================
# CONFIGURACIÓN DE ALERTAS
# ============================================

st.header("⚙️ Configuración de Alertas")

with st.expander("Ajustar umbrales de alertas"):
    st.markdown("""
    Los umbrales actuales están configurados según las mejores prácticas del sector.
    Si deseas personalizarlos, modifica el archivo `utils/config.py`.
    """)
    
    # Mostrar umbrales actuales
    st.markdown("#### Umbrales Actuales")
    
    umbrales_df = []
    for id_metrica, umbral in UMBRALES.items():
        umbrales_df.append({
            'Métrica': umbral['nombre'],
            'Óptimo': umbral['optimo'],
            'Precaución': umbral['precaucion'],
            'Crítico': umbral['critico'],
            'Tipo': 'Menor es mejor' if umbral.get('tipo') == 'menor_mejor' else 'Mayor es mejor'
        })
    
    df_umbrales = pd.DataFrame(umbrales_df)
    
    st.dataframe(
        df_umbrales,
        hide_index=True,
        use_container_width=True
    )

# ============================================
# EXPORTAR REPORTE DE ALERTAS
# ============================================

st.markdown("---")

if st.button("📥 Exportar Reporte de Alertas", type="primary"):
    # Crear reporte
    reporte = f"""
REPORTE DE ALERTAS - SUSTAINABLE GROWTH MONITOR
Fecha de generación: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}
Período analizado: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}

========================================
RESUMEN EJECUTIVO
========================================

🔴 Alertas Críticas: {len(estados['critical'])}
🟡 Alertas de Precaución: {len(estados['warning'])}
🟢 Métricas Óptimas: {len(estados['optimal'])}

========================================
ALERTAS CRÍTICAS
========================================

"""
    
    if len(estados['critical']) > 0:
        for alerta in estados['critical']:
            reporte += f"\n{alerta['metrica']}\n"
            reporte += f"  Valor: {formatear_valor(alerta['valor'], alerta['unidad'])}\n"
            reporte += f"  Área: {alerta['area']}\n"
            
            recomendacion = obtener_recomendacion(alerta['id_metrica'], 'critical')
            if recomendacion:
                reporte += f"  Recomendación: {recomendacion}\n"
    else:
        reporte += "\nNo hay alertas críticas.\n"
    
    reporte += """
========================================
ALERTAS DE PRECAUCIÓN
========================================

"""
    
    if len(estados['warning']) > 0:
        for alerta in estados['warning']:
            reporte += f"\n{alerta['metrica']}\n"
            reporte += f"  Valor: {formatear_valor(alerta['valor'], alerta['unidad'])}\n"
            reporte += f"  Área: {alerta['area']}\n"
    else:
        reporte += "\nNo hay alertas de precaución.\n"
    
    # Descargar
    st.download_button(
        label="💾 Descargar Reporte (TXT)",
        data=reporte.encode('utf-8'),
        file_name=f'reporte_alertas_{pd.Timestamp.now().strftime("%Y%m%d_%H%M")}.txt',
        mime='text/plain'
    )

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.caption("⚠️ Sistema de Alertas | Sustainable Growth Monitor")
st.caption(f"📊 Última actualización: {fecha_ultimo.strftime('%d/%m/%Y')}")
st.caption("🔔 Revisa esta página diariamente para mantener tus métricas bajo control")