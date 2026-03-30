"""
ETL: Load - Carga de datos a DuckDB
"""

import duckdb
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime

# ============================================
# CONFIGURACIÓN
# ============================================

DATA_CURATED = Path("data/curated")
DATABASE_DIR = Path("database")
SCHEMA_FILE = DATABASE_DIR / "schema.sql"
DB_FILE = DATABASE_DIR / "technova.duckdb"

# ============================================
# FUNCIONES
# ============================================

def log(msg, level="INFO"):
    """Función simple de logging"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}")


def ejecutar_schema(conn):
    """Ejecuta el archivo schema.sql"""
    if not SCHEMA_FILE.exists():
        log(f"Archivo schema no encontrado: {SCHEMA_FILE}", "ERROR")
        sys.exit(1)
    
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    try:
        conn.execute(schema_sql)
        log("Schema ejecutado correctamente")
    except Exception as e:
        log(f"Error ejecutando schema: {e}", "ERROR")
        sys.exit(1)


def cargar_tabla(conn, tabla, csv_path, columnas):
    """Carga una tabla con full-refresh (DELETE + INSERT)"""
    if not csv_path.exists():
        log(f"  ⚠️  Archivo no encontrado: {csv_path}", "WARNING")
        return 0
    
    df = pd.read_csv(csv_path, encoding='utf-8')
    
    if df.empty:
        log(f"  ⚠️  Archivo vacío: {csv_path}", "WARNING")
        return 0
    
    # DELETE
    conn.execute(f"DELETE FROM {tabla}")
    
    # INSERT
    conn.register('temp_df', df)
    columnas_str = ', '.join(columnas)
    conn.execute(f"""
        INSERT INTO {tabla} ({columnas_str})
        SELECT {columnas_str} FROM temp_df
    """)
    
    resultado = conn.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()
    count = resultado[0]
    
    log(f"  ✅ {tabla}: {count:,} filas cargadas")
    return count


def verificar_fk(conn):
    """Verifica que no haya registros huérfanos en fact_monitoreo"""
    log("\n🔍 Verificando integridad de claves foráneas...")
    
    verificaciones = [
        ('id_tiempo', 'dim_tiempo'),
        ('id_metrica', 'dim_metrica'),
        ('id_area', 'dim_area')
    ]
    
    todo_ok = True
    
    for fk_col, dim_tabla in verificaciones:
        query = f"""
            SELECT COUNT(*) FROM fact_monitoreo f
            LEFT JOIN {dim_tabla} d ON f.{fk_col} = d.{fk_col}
            WHERE d.{fk_col} IS NULL
        """
        result = conn.execute(query).fetchone()
        huerfanos = result[0]
        
        if huerfanos > 0:
            log(f"  ❌ {fk_col}: {huerfanos} registros huérfanos", "ERROR")
            todo_ok = False
        else:
            log(f"  ✅ {fk_col}: sin huérfanos")
    
    return todo_ok


def guardar_metadata(conn, resultados):
    """Guarda el registro de la carga"""
    # Crear tabla con SERIAL (autoincremental)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS metadata_carga (
            id INTEGER PRIMARY KEY,
            fecha TIMESTAMP,
            tabla VARCHAR,
            filas INTEGER
        )
    """)
    
    # Insertar sin especificar ID (DuckDB no soporta autoincrement directamente)
    # Alternativa: usar SEQUENCE
    conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_metadata START 1")
    
    for tabla, filas in resultados.items():
        conn.execute("""
            INSERT INTO metadata_carga (id, fecha, tabla, filas)
            VALUES (nextval('seq_metadata'), ?, ?, ?)
        """, [datetime.now(), tabla, filas])
    
    log("  📝 Metadatos guardados en metadata_carga")


# ============================================
# MAIN
# ============================================

def main():
    log("=" * 60)
    log("🚀 INICIANDO CARGA A DUCKDB")
    log("=" * 60)
    
    # 1. Crear directorio si no existe
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    
    # 2. Conectar a DuckDB
    conn = duckdb.connect(str(DB_FILE))
    log(f"✅ Conectado a: {DB_FILE}")
    
    # 3. Ejecutar schema.sql
    ejecutar_schema(conn)
    
    # 4. Definir tablas
    tablas = {
        'fact_monitoreo': {
            'csv': DATA_CURATED / 'fact_monitoreo.csv',
            'columnas': ['id_monitoreo', 'id_tiempo', 'id_metrica', 'id_area', 'valor', 'fuente']
        },
        'dim_tiempo': {
            'csv': DATA_CURATED / 'dim_tiempo.csv',
            'columnas': ['id_tiempo', 'fecha', 'anio', 'mes', 'dia', 
                        'trimestre', 'semana', 'nombre_mes', 'dia_semana', 'es_finde']
        },
        'dim_area': {
            'csv': DATA_CURATED / 'dim_area.csv',
            'columnas': ['id_area', 'nombre_area']
        },
        'dim_metrica': {
            'csv': DATA_CURATED / 'dim_metrica.csv',
            'columnas': ['id_metrica', 'nombre', 'categoria', 'subcategoria', 'unidad', 'descripcion']
        },
        'dim_empleado': {
            'csv': DATA_CURATED / 'dim_empleado.csv',
            'columnas': ['id_empleado', 'nombre', 'area', 'genero', 'fecha_ingreso']
        },
        'dim_proveedor': {
            'csv': DATA_CURATED / 'dim_proveedor.csv',
            'columnas': ['id_proveedor', 'nombre_proveedor']
        }
    }
    
    # 5. Cargar en orden específico
    log("\n📤 EJECUTANDO FULL-REFRESH...")
    resultados = {}
    
    #orden_carga = ['fact_monitoreo', 'dim_tiempo', 'dim_area', 'dim_metrica', 'dim_empleado', 'dim_proveedor']
    orden_carga = ['dim_tiempo', 'dim_area', 'dim_metrica', 'dim_empleado', 'dim_proveedor', 'fact_monitoreo']
    for tabla in orden_carga:
        if tabla in tablas:
            log(f"\n📁 {tabla}")
            config = tablas[tabla]
            filas = cargar_tabla(conn, tabla, config['csv'], config['columnas'])
            resultados[tabla] = filas
        else:
            log(f"⚠️  Tabla {tabla} no encontrada", "WARNING")
    
    # 6. Verificar integridad FK
    fk_ok = verificar_fk(conn)
    
    # 7. Guardar metadata
    guardar_metadata(conn, resultados)
    
    # 8. Resumen final
    log("\n" + "=" * 60)
    log("✅ CARGA COMPLETADA")
    log("=" * 60)
    log("\n📊 RESUMEN DE FILAS CARGADAS:")
    
    for tabla, filas in resultados.items():
        log(f"   • {tabla}: {filas:,} filas")
    
    if not fk_ok:
        log("\n⚠️  ADVERTENCIA: Problemas de integridad referencial detectados", "WARNING")
    
    log(f"\n💾 Base de datos: {DB_FILE}")
    
    conn.close()


# ============================================
# EJECUCIÓN
# ============================================

if __name__ == "__main__":
    main()