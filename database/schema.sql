-- ============================================
-- SCHEMA: Sustainable Growth Monitor
-- Base de datos: technova.duckdb
-- ============================================

-- ------------------------------------------------------------
-- 1. DIMENSIÓN TIEMPO
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_tiempo (
    id_tiempo INTEGER PRIMARY KEY,
    fecha DATE NOT NULL,
    anio INTEGER,
    mes INTEGER,
    dia INTEGER,
    trimestre INTEGER,
    semana INTEGER,
    nombre_mes VARCHAR,
    dia_semana VARCHAR,
    es_finde BOOLEAN
);

-- ------------------------------------------------------------
-- 2. DIMENSIÓN ÁREA
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_area (
    id_area INTEGER PRIMARY KEY,
    nombre_area VARCHAR NOT NULL
);

-- ------------------------------------------------------------
-- 3. DIMENSIÓN MÉTRICA
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_metrica (
    id_metrica INTEGER PRIMARY KEY,
    nombre VARCHAR NOT NULL,
    categoria VARCHAR,
    subcategoria VARCHAR,
    unidad VARCHAR,
    descripcion VARCHAR
);

-- ------------------------------------------------------------
-- 4. DIMENSIÓN EMPLEADO
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_empleado (
    id_empleado VARCHAR PRIMARY KEY,
    nombre VARCHAR,
    area VARCHAR,
    genero VARCHAR,
    fecha_ingreso DATE
);

-- ------------------------------------------------------------
-- 5. DIMENSIÓN PROVEEDOR
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_proveedor (
    id_proveedor INTEGER PRIMARY KEY,
    nombre_proveedor VARCHAR NOT NULL
);

-- ------------------------------------------------------------
-- 6. TABLA DE HECHOS: FACT_MONITOREO
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_monitoreo (
    id_monitoreo INTEGER PRIMARY KEY,
    id_tiempo INTEGER NOT NULL,
    id_metrica INTEGER NOT NULL,
    id_area INTEGER NOT NULL,
    valor DOUBLE,
    fuente VARCHAR,
    FOREIGN KEY (id_tiempo) REFERENCES dim_tiempo(id_tiempo),
    FOREIGN KEY (id_metrica) REFERENCES dim_metrica(id_metrica),
    FOREIGN KEY (id_area) REFERENCES dim_area(id_area)
);

-- ------------------------------------------------------------
-- 7. ÍNDICES PARA RENDIMIENTO
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_tiempo ON fact_monitoreo(id_tiempo);
CREATE INDEX IF NOT EXISTS idx_fact_metrica ON fact_monitoreo(id_metrica);
CREATE INDEX IF NOT EXISTS idx_fact_area ON fact_monitoreo(id_area);