"""
🗄️ DuckDB Repository Implementation
"""

import duckdb
import pandas as pd
import streamlit as st
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

from core import DataRepository, FilterConfig, MetricConfig

# ============================================
# DUCKDB REPOSITORY (Singleton)
# ============================================

class DuckDBRepository(DataRepository):
    """Implementación del Repository para DuckDB"""
    
    _instance = None
    _connection = None
    
    def __new__(cls, db_path: str):
        if cls._instance is None:
            cls._instance = super(DuckDBRepository, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, db_path: str):
        if self._connection is None:
            self.db_path = Path(db_path)
            self._connect()
    
    def _connect(self):
        """Establece conexión con DuckDB"""
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        
        self._connection = duckdb.connect(str(self.db_path), read_only=True)
    
    def _get_connection(self):
        """Obtiene la conexión"""
        if self._connection is None:
            self._connect()
        return self._connection
    
    @st.cache_data(ttl=60)
    def get_fact_monitoreo(_self, filtros: FilterConfig) -> pd.DataFrame:
        """Obtiene datos de fact_monitoreo"""
        conn = _self._get_connection()
        
        query = """
            SELECT 
                f.id_monitoreo,
                f.id_tiempo,
                f.id_metrica,
                f.id_area,
                f.valor,
                f.fuente,
                t.fecha,
                t.anio,
                t.mes,
                t.trimestre,
                m.nombre as metrica,
                m.categoria,
                m.unidad,
                a.nombre_area
            FROM fact_monitoreo f
            JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo
            JOIN dim_metrica m ON f.id_metrica = m.id_metrica
            JOIN dim_area a ON f.id_area = a.id_area
            WHERE 1=1
        """
        
        params = []
        
        if filtros.fecha_inicio:
            query += " AND t.fecha >= ?"
            params.append(filtros.fecha_inicio)
        
        if filtros.fecha_fin:
            query += " AND t.fecha <= ?"
            params.append(filtros.fecha_fin)
        
        if filtros.categoria:
            query += " AND m.categoria = ?"
            params.append(filtros.categoria)
        
        if filtros.area:
            query += " AND a.nombre_area = ?"
            params.append(filtros.area)
        
        query += " ORDER BY t.fecha, m.id_metrica"
        
        df = conn.execute(query, params).df()
        
        if not df.empty:
            df['fecha'] = pd.to_datetime(df['fecha'])
        
        return df
    
    @st.cache_data(ttl=300)
    def get_date_range(_self) -> Tuple[datetime, datetime]:
        """Obtiene rango de fechas"""
        conn = _self._get_connection()
        
        query = "SELECT MIN(fecha) as fecha_min, MAX(fecha) as fecha_max FROM dim_tiempo"
        result = conn.execute(query).fetchone()
        
        return pd.to_datetime(result[0]), pd.to_datetime(result[1])
    
    @st.cache_data(ttl=300)
    def get_metricas(_self) -> List[MetricConfig]:
        """Obtiene catálogo de métricas"""
        conn = _self._get_connection()
        
        query = """
            SELECT 
                id_metrica,
                nombre,
                categoria,
                unidad,
                descripcion
            FROM dim_metrica
            ORDER BY id_metrica
        """
        
        df = conn.execute(query).df()
        
        colores = {
            'Financiera': '#1f77b4',
            'E': '#2ca02c',
            'S': '#ff7f0e'
        }
        
        metricas = []
        for _, row in df.iterrows():
            metricas.append(MetricConfig(
                id=row['id_metrica'],
                nombre=row['nombre'],
                categoria=row['categoria'],
                unidad=row['unidad'],
                color=colores.get(row['categoria'], '#9467bd'),
                descripcion=row['descripcion']
            ))
        
        return metricas
    
    @st.cache_data(ttl=300)
    def get_areas(_self) -> List[str]:
        """Obtiene lista de áreas"""
        conn = _self._get_connection()
        
        query = """
            SELECT nombre_area
            FROM dim_area
            WHERE nombre_area != 'Todas'
            ORDER BY nombre_area
        """
        
        df = conn.execute(query).df()
        return df['nombre_area'].tolist()
    
    @st.cache_data(ttl=300)
    def get_empleados(_self) -> pd.DataFrame:
        """Obtiene información de empleados"""
        conn = _self._get_connection()
        
        query = """
            SELECT 
                id_empleado,
                nombre,
                area,
                genero,
                fecha_ingreso
            FROM dim_empleado
            ORDER BY nombre
        """
        
        df = conn.execute(query).df()
        
        if not df.empty and 'fecha_ingreso' in df.columns:
            df['fecha_ingreso'] = pd.to_datetime(df['fecha_ingreso'])
        
        return df

# ============================================
# REPOSITORY FACTORY
# ============================================

class RepositoryFactory:
    """Factory para crear instancias del Repository"""
    
    @staticmethod
    def create(tipo: str = "duckdb", **kwargs) -> DataRepository:
        if tipo == "duckdb":
            db_path = kwargs.get('db_path', 'database/technova.duckdb')
            return DuckDBRepository(db_path)
        else:
            raise ValueError(f"Tipo de repository no soportado: {tipo}")