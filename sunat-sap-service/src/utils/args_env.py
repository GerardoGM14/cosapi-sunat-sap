import os
from pathlib import Path
from dotenv import load_dotenv
from src.schemas.IConfig import IArgs


def get_args_env() -> IArgs:
    load_dotenv()

    folder = os.getenv("FOLDER")
    if not folder:
        raise ValueError("La variable de entorno FOLDER no está definida.")

    date_str = os.getenv("DATE")
    if not date_str:
        raise ValueError("La variable de entorno DATE no está definida.")

    month = int(date_str.split("/")[1])
    year = int(date_str.split("/")[2])

    folder_sap = Path(folder) / 'sap'
    folder_sunat = Path(folder) / 'sunat'

    return {
        'sap': {
            'code_sociedad': os.getenv("CODE_SOCIEDAD"),
            'date': date_str,
            'folder': str(folder_sap),
            'cred': {
                'email': os.getenv("CORREO_SAP"),
                'password': os.getenv("PASSWORD_SAP")
            }
        },
        'sunat': {
            'date': {
                'month': month,
                'year': year
            },
            'folder': str(folder_sunat),
            'cred': {
                'ruc': os.getenv("RUC_SUNAT"),
                'user': os.getenv("USER_SUNAT"),
                'clave': os.getenv("PASSWORD_SUNAT")
            }
        }
    }


if __name__ == '__main__':    
    try:
        args = get_args_env()
        print(args)
    except (ValueError, TypeError) as e:
        print(f"Error: {e}")
        print("Asegúrate de que el archivo .env exista y contenga todas las variables requeridas.")
