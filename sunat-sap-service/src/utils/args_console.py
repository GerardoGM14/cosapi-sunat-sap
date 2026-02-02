import argparse
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

    # ARGUMENTO OPTIONAL
    parser.add_argument(
        "--socket_url",
        type=str,
        default="ws://localhost:3000",
        help="URL del socket para la conexión"
    )

    month = int(parser.parse_args().date.split("/")[1])
    year = int(parser.parse_args().date.split("/")[2])

    folder = parser.parse_args().folder

    folder_sap = Path(folder) / 'sap'

    folder_sunat = Path(folder) / 'sunat'

    return {
        'sap': {
            'code_sociedad': parser.parse_args().code_sociedad,
            'date': parser.parse_args().date,
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
            'folder': str(folder_sunat),
            'cred': {
                'ruc': parser.parse_args().ruc_sunat,
                'user': parser.parse_args().user_sunat,
                'clave': parser.parse_args().password_sunat
            }
        },
        'socket_url': parser.parse_args().socket_url
    }
