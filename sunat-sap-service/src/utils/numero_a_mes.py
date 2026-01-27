from src.schemas.IReturn import IReturn
from typing import Union


def numero_a_mes(num_month: Union[int, str]) -> IReturn:
    abreviaturas = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SET', 'OCT', 'NOV', 'DIC']
    nombres_completos = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    try:
        num = int(num_month)
        if 1 <= num <= 12:
            return {
                'success': True,
                'message': '✅ Mes obtenido correctamente.',
                'abreviatura_opt': abreviaturas[num - 1],
                'nombre_completo_mes_opt': nombres_completos[num - 1]
            }
        else:
            return {
                'success': False,
                'message': '⚠️ El número debe estar entre 1 y 12.',
            }
    except ValueError:
        return {
            'success': False,
            'message': '❌ Entrada inválida. Debe ser un número.',
        }