import argparse
import sys
from pathlib import Path
from src.schemas.IConfig import IArgs


def get_args_console() -> IArgs:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--folder",
        type=str,
        required=True,
        help="Ruta de la carpeta donde se guardarán los archivos"
    )

    parser.add_argument(
        "--code_sociedad",
        type=str,
        required=True,
        help="Código de la sociedad como PE01, PE02, etc."
    )

    parser.add_argument(
        "--date",
        type=str,
        required=True,
        help="Fecha en formato dd/mm/yyyy"
    )

    parser.add_argument(
        "--ruc_sunat",
        type=str,
        required=True,
        help="RUC para ingresar a la plataforma SUNAT"
    )

    parser.add_argument(
        "--user_sunat",
        type=str,
        required=True,
        help="Usuario para ingresar a la plataforma SUNAT"
    )

    parser.add_argument(
        "--password_sunat",
        type=str,
        required=True,
        help="Contraseña para ingresar a la plataforma SUNAT"
    )

    parser.add_argument(
        "--correo_sap",
        type=str,
        required=True,
        help="Correo para ingresar a la plataforma SAP"
    )

    parser.add_argument(
        "--password_sap",
        type=str,
        required=True,
        help="Contraseña para ingresar a la plataforma SAP"
    )
    
    parser.add_argument(
        "--time",
        type=str,
        required=False,
        default=None,
        help="Hora de ejecución programada (formato HH:MM)"
    )

    parser.add_argument(
        "--days",
        type=str,
        required=False,
        default=None,
        help="Días programados (ej: L,M,M,J,V,S,D)"
    )

    default_socket_url = "http://localhost:8001"
    
    if sys.platform != "win32":
        try:
            import socket
            socket.gethostbyname("backend")
            default_socket_url = "http://backend:8001"
        except:
            try:
                import socket
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                default_socket_url = f"http://{local_ip}:8001"
            except:
                default_socket_url = "http://localhost:8001"

    parser.add_argument(
        "--socket_url",
        type=str,
        default=default_socket_url,
        help="URL del socket para la conexión"
    )

    month = int(parser.parse_args().date.split("/")[1])
    year = int(parser.parse_args().date.split("/")[2])

    folder = parser.parse_args().folder

    folder_sap = Path(folder) / 'sap'

    folder_sunat = Path(folder) / 'sunat'

    time_arg = parser.parse_args().time
    days_arg = parser.parse_args().days

    return {
        'sap': {
            'code_sociedad': parser.parse_args().code_sociedad,
            'date': parser.parse_args().date,
            'time': time_arg,
            'days': days_arg,
            'folder': str(folder_sap),
            'cred': {
                'email': parser.parse_args().correo_sap,
                'password': parser.parse_args().password_sap
            }
        },
        'sunat': {
            'date': {
                'month': month,
                'year': year
            },
            'time': time_arg,
            'days': days_arg,
            'folder': str(folder_sunat),
            'cred': {
                'ruc': parser.parse_args().ruc_sunat,
                'user': parser.parse_args().user_sunat,
                'clave': parser.parse_args().password_sunat
            },
            'input_date': parser.parse_args().date
        },
        'socket_url': parser.parse_args().socket_url
    }
