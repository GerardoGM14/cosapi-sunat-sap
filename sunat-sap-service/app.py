import asyncio
from src.sap import appSap
from src.sunat import appSunat
from src.config.manager_args import get_args


argsAll = get_args()

result = asyncio.run(appSap(args=argsAll['sap']))

print("")
print("="*50)
print("Resultado de appSap:\n")
for key, value in result.items():
     print(f"{key}: {value}")

result = asyncio.run(appSunat(args=argsAll['sunat']))

print("")
print("="*50)
print("Resultado de appSunat:\n")
for key, value in result.items():
    print(f"{key}: {value}")