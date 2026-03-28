"""
Carga simple de los 7 archivos CSV del proyecto
Sustainable Growth Monitor
"""

import pandas as pd
import os
from pathlib import Path

# Configuración
DATA_RAW = "data/raw"
DATA_PROCESSED = "data/processed"

# Crear carpeta de salida
Path(DATA_PROCESSED).mkdir(parents=True, exist_ok=True)

# Lista de archivos a cargar
archivos = [
    "compras_proveedor.csv",
    "consumo_energetico.csv",
    "encuestas_clima.csv",
    "eventos_rrhh.csv",
    "personal_nomina.csv",
    "residuos_reciclaje.csv",
    "ventas_transacciones.csv",
]

# Diccionario para guardar los dataframes
datos = {}

print("=" * 50)
print("CARGANDO ARCHIVOS...")
print("=" * 50)

# ============================================
# 1. COMPRAS PROVEEDOR
# ============================================
print("\n📁 Cargando compras_proveedor.csv...")
try:
    df = pd.read_csv(f"{DATA_RAW}/compras_proveedor.csv")
    df["fecha_emision"] = pd.to_datetime(df["fecha_emision"])
    df["fecha_pago"] = pd.to_datetime(df["fecha_pago"])
    datos["compras"] = df
    print(f"   ✅ {len(df)} registros cargados")
except Exception as e:
    print(f"   ❌ Error: {e}")

# ============================================
# 2. CONSUMO ENERGÉTICO
# ============================================
print("\n📁 Cargando consumo_energetico.csv...")
try:
    df = pd.read_csv(f"{DATA_RAW}/consumo_energetico.csv")
    df["fecha"] = pd.to_datetime(df["fecha"])

    # Crear columna de kWh totales (gas convertido)
    df["kwh_totales"] = df["kwh_consumidos"] + (df["m3_gas"] * 10.69)

    datos["consumo_energetico"] = df
    print(f"   ✅ {len(df)} registros cargados")
    print(f"   📊 kWh totales calculados (gas → kWh)")
except Exception as e:
    print(f"   ❌ Error: {e}")

# ============================================
# 3. ENCUESTAS CLIMA
# ============================================
print("\n📁 Cargando encuestas_clima.csv...")
try:
    df = pd.read_csv(f"{DATA_RAW}/encuestas_clima.csv")
    df["fecha_encuesta"] = pd.to_datetime(df["fecha_encuesta"])
    datos["encuestas"] = df
    print(f"   ✅ {len(df)} registros cargados")
except Exception as e:
    print(f"   ❌ Error: {e}")

# ============================================
# 4. EVENTOS RRHH
# ============================================
print("\n📁 Cargando eventos_rrhh.csv...")
try:
    df = pd.read_csv(f"{DATA_RAW}/eventos_rrhh.csv")
    df["fecha"] = pd.to_datetime(df["fecha"])
    datos["eventos_rrhh"] = df
    print(f"   ✅ {len(df)} registros cargados")
except Exception as e:
    print(f"   ❌ Error: {e}")

# ============================================
# 5. PERSONAL NÓMINA (con manejo de comillas)
# ============================================
print("\n📁 Cargando personal_nomina.csv (formato especial)...")
try:
    # Leer con manejo especial de comillas
    df = pd.read_csv(
        f"{DATA_RAW}/personal_nomina.csv",
        quoting=1,  # QUOTE_ALL
        doublequote=True,  # Convierte "" en "
        encoding="utf-8",
    )

    # Limpiar comillas sobrantes
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].str.replace('"', "", regex=False)

    # Convertir fechas
    df["mes"] = pd.to_datetime(df["mes"])
    df["fecha_ingreso"] = pd.to_datetime(df["fecha_ingreso"])

    datos["personal_nomina"] = df
    print(f"   ✅ {len(df)} registros cargados")
    print(f"   🔧 Formato con comillas anidadas procesado correctamente")
except Exception as e:
    print(f"   ❌ Error: {e}")

# ============================================
# 6. RESIDUOS RECICLAJE
# ============================================
print("\n📁 Cargando residuos_reciclaje.csv...")
try:
    df = pd.read_csv(f"{DATA_RAW}/residuos_reciclaje.csv")
    df["fecha_semana"] = pd.to_datetime(df["fecha_semana"])

    # Calcular tasa de reciclaje
    df["tasa_reciclaje"] = (df["kg_reciclados"] / df["kg_generados"]) * 100

    datos["residuos"] = df
    print(f"   ✅ {len(df)} registros cargados")
    print(f"   📊 Tasa de reciclaje calculada")
except Exception as e:
    print(f"   ❌ Error: {e}")

# ============================================
# 7. VENTAS TRANSACCIONES
# ============================================
print("\n📁 Cargando ventas_transacciones.csv...")
try:
    df = pd.read_csv(f"{DATA_RAW}/ventas_transacciones.csv")
    df["fecha"] = pd.to_datetime(df["fecha"])
    datos["ventas"] = df
    print(f"   ✅ {len(df)} registros cargados")
except Exception as e:
    print(f"   ❌ Error: {e}")

# ============================================
# GUARDAR ARCHIVOS PROCESADOS
# ============================================
print("\n" + "=" * 50)
print("GUARDANDO ARCHIVOS PROCESADOS...")
print("=" * 50)

for nombre, df in datos.items():
    output_file = f"{DATA_PROCESSED}/{nombre}_clean.csv"
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"   💾 {nombre}_clean.csv guardado ({len(df)} registros)")

# ============================================
# RESUMEN FINAL
# ============================================
print("\n" + "=" * 50)
print("✅ CARGA COMPLETADA")
print("=" * 50)
print(f"\n📊 Dataframes cargados:")
for nombre, df in datos.items():
    print(f"   • {nombre}: {len(df):,} filas, {len(df.columns)} columnas")

print(f"\n📁 Archivos guardados en: {DATA_PROCESSED}/")
print("\n🔍 Puedes acceder a los datos con:")
print("   datos['ventas']          # Ventas")
print("   datos['compras']         # Compras")
print("   datos['personal_nomina'] # Nómina")
print("   datos['consumo_energetico'] # Energía")
print("   datos['residuos']        # Residuos")
print("   datos['encuestas']       # Encuestas")
print("   datos['eventos_rrhh']    # Eventos RRHH")
