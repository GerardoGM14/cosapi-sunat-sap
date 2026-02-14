import time
import os
import json
import shutil
import asyncio
from pathlib import Path
from src.sap import appSap
from src.sunat import appSunat
from src.socket_client.manager import socket_manager
from src.logger.colored_logger import ColoredLogger, Colors

logger = ColoredLogger()

# Configuración de carpetas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # dmz/sunat-sap-service
DMZ_ROOT = os.path.dirname(BASE_DIR) # dmz
EXCHANGE_DIR = os.path.join(DMZ_ROOT, "exchange")

PENDING_DIR = os.path.join(EXCHANGE_DIR, "pendientes")
PROCESSED_DIR = os.path.join(EXCHANGE_DIR, "procesados")
ERROR_DIR = os.path.join(EXCHANGE_DIR, "errores")

# Asegurar que existan
os.makedirs(PENDING_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(ERROR_DIR, exist_ok=True)

async def process_job(job_file, job_data):
    logger.log(f"🔄 Procesando trabajo: {job_file}", Colors.BLUE)
    
    # Iniciar conexión Socket si es necesario
    socket_url = job_data.get('socket_url', 'http://localhost:8001')
    try:
        socket_manager.initialize(server_url=socket_url)
        socket_manager.connect()
    except Exception as e:
        logger.log(f"⚠️ No se pudo conectar al socket: {e}", Colors.YELLOW)

    try:
        # Ejecutar SAP
        if 'sap' in job_data:
            logger.log("⚙️ Iniciando appSap...", Colors.BLUE)
            await appSap(args=job_data['sap'])
            logger.log("✅ appSap finalizado", Colors.GREEN)

        # Ejecutar SUNAT
        if 'sunat' in job_data:
            logger.log("⚙️ Iniciando appSunat...", Colors.BLUE)
            await appSunat(args=job_data['sunat'])
            logger.log("✅ appSunat finalizado", Colors.GREEN)

        return True
    except Exception as e:
        logger.log(f"❌ Error en la ejecución: {e}", Colors.RED)
        return False
    finally:
        socket_manager.disconnect()

def main():
    logger.log(f"👀 Watcher iniciado. Vigilando: {PENDING_DIR}", Colors.CYAN)
    logger.log("Esperando archivos JSON...", Colors.CYAN)

    while True:
        try:
            # Listar archivos JSON en pendientes
            files = [f for f in os.listdir(PENDING_DIR) if f.endswith('.json')]
            
            for filename in files:
                file_path = os.path.join(PENDING_DIR, filename)
                
                # Intentar leer el archivo
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        job_data = json.load(f)
                    
                    # Ejecutar trabajo
                    success = asyncio.run(process_job(filename, job_data))
                    
                    # Mover archivo según resultado
                    if success:
                        shutil.move(file_path, os.path.join(PROCESSED_DIR, filename))
                        logger.log(f"✅ Trabajo completado y movido a procesados: {filename}", Colors.GREEN)
                    else:
                        shutil.move(file_path, os.path.join(ERROR_DIR, filename))
                        logger.log(f"❌ Trabajo fallido y movido a errores: {filename}", Colors.RED)
                        
                except json.JSONDecodeError:
                    logger.log(f"⚠️ Archivo JSON inválido: {filename}", Colors.RED)
                    shutil.move(file_path, os.path.join(ERROR_DIR, filename))
                except Exception as e:
                    logger.log(f"⚠️ Error procesando archivo {filename}: {e}", Colors.RED)
                    # Intentar mover a errores si no está bloqueado
                    try:
                        shutil.move(file_path, os.path.join(ERROR_DIR, filename))
                    except:
                        pass

            time.sleep(2) # Esperar 2 segundos antes de volver a escanear
            
        except KeyboardInterrupt:
            logger.log("\n👋 Watcher detenido por el usuario.", Colors.YELLOW)
            break
        except Exception as e:
            logger.log(f"💥 Error crítico en el loop principal: {e}", Colors.RED)
            time.sleep(5)

if __name__ == "__main__":
    main()
