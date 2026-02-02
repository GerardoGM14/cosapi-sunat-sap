import os
from dotenv import load_dotenv

load_dotenv()


class ConfigEnv:
    FOLDER = os.getenv('FOLDER')
    DATE = os.getenv('DATE')
    CODE_SOCIEDAD = os.getenv('CODE_SOCIEDAD')
    CORREO_SAP = os.getenv('CORREO_SAP')
    PASSWORD_SAP = os.getenv('PASSWORD_SAP')
    RUC_SUNAT = os.getenv('RUC_SUNAT')
    USER_SUNAT = os.getenv('USER_SUNAT')
    PASSWORD_SUNAT = os.getenv('PASSWORD_SUNAT')
    CONFIG_METHOD = os.getenv('CONFIG_METHOD')
    SOCKET_URL = os.getenv('SOCKET_URL')
