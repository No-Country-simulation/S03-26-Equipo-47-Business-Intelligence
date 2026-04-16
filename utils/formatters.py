"""
🛠️ Utilidades de Formateo
"""

def formatear_valor(valor: float, unidad: str) -> str:
    """Formatea un valor según su unidad"""
    
    if unidad == 'ARS':
        if abs(valor) >= 1_000_000:
            return f"${valor/1_000_000:.1f}M"
        elif abs(valor) >= 1_000:
            return f"${valor/1_000:.1f}K"
        else:
            return f"${valor:.0f}"
    
    elif unidad == 'kWh':
        if abs(valor) >= 1_000:
            return f"{valor/1_000:.1f}K kWh"
        else:
            return f"{valor:.0f} kWh"
    
    elif unidad == '%':
        return f"{valor:.1f}%"
    
    elif unidad == 'puntos':
        return f"{valor:.1f} pts"
    
    elif unidad in ['horas', 'días']:
        return f"{valor:.0f} {unidad}"
    
    else:
        return f"{valor:.2f} {unidad}"