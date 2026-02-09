import asyncio
from src.sap import appSap
from src.sunat import appSunat
from src.config.manager_args import get_args
from src.socket_client.manager import socket_manager
from src.logger.colored_logger import ColoredLogger, Colors

logger = ColoredLogger()

argsAll = get_args()

socket_manager.initialize(server_url=argsAll['socket_url'])
socket_manager.connect()

logger.log("⚙️ Iniciando appSap...", Colors.BLUE)
result = asyncio.run(appSap(args=argsAll['sap']))

print("")
print("="*50)
print("Resultado de appSap:\n")
for key, value in result.items():
    print(f"{key}: {value}")

logger.log("⚙️ Iniciando appSunat...", Colors.BLUE)
result = asyncio.run(appSunat(args=argsAll['sunat']))

print("")
print("="*50)
print("Resultado de appSunat:\n")
for key, value in result.items():
    print(f"{key}: {value}")


socket_manager.disconnect()

logger.log("⚙️ Cerrando conexión con el socket...", Colors.BLUE)
