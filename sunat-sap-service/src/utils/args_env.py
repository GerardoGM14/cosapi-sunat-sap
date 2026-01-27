from pathlib import Path
from src.schemas.IConfig import IArgs
from src.config.config_env import ConfigEnv


def get_args_env() -> IArgs:

    folder = ConfigEnv.FOLDER
    if not folder:
        raise ValueError(f"La variable de entorno FOLDER no está definida.")

    date_str = ConfigEnv.DATE
    if not date_str:
        raise ValueError(f"La variable de entorno DATE no está definida.")

    month = int(date_str.split("/")[1])
    year = int(date_str.split("/")[2])

    folder_sap = Path(folder) / 'sap'
    folder_sunat = Path(folder) / 'sunat'

    return {
        'sap': {
            'code_sociedad': ConfigEnv.CODE_SOCIEDAD,
            'date': date_str,
            'folder': str(folder_sap),
            'cred': {
                'email': ConfigEnv.CORREO_SAP,
                'password': ConfigEnv.PASSWORD_SAP
            }
        },
        'sunat': {
            'date': {
                'month': month,
                'year': year
            },
            'folder': str(folder_sunat),
            'cred': {
                'ruc': ConfigEnv.RUC_SUNAT,
                'user': ConfigEnv.USER_SUNAT,
                'clave': ConfigEnv.PASSWORD_SUNAT
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
