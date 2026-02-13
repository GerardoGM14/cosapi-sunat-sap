from datetime import datetime, timedelta


def procesar_fecha(fecha: str, dias: int = 4) -> tuple[str, str]:
    try:
        fecha_obj = datetime.strptime(fecha, "%d/%m/%Y")

        delta = timedelta(days=dias)
        fecha_inicio_obj = fecha_obj - delta
        fecha_fin_obj = fecha_obj + delta

        formato_salida = "%d/%m/%Y"
        fecha_inicio_str = fecha_inicio_obj.strftime(formato_salida)
        fecha_fin_str = fecha_fin_obj.strftime(formato_salida)
        inicio = fecha_inicio_str.replace("/", ".")
        fin = fecha_fin_str.replace("/", ".")
        
        inicio = inicio[6:] + inicio[3:5] + inicio[:2]
        fin = fin[6:] + fin[3:5] + fin[:2]

        return inicio, fin
    except ValueError as ve:
        return f"Error: {ve}"
