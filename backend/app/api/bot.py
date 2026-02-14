from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess
import sys
import os
import asyncio
import threading
from datetime import datetime
from app.socket_manager import sio
from app.database import SessionLocal
from app.models import DSeguimiento

router = APIRouter()

class SunatConfig(BaseModel):
    ruc: str
    usuario: str
    claveSol: str

class SapConfig(BaseModel):
    usuario: str
    password: str

class GeneralConfig(BaseModel):
    sociedad: str
    fecha: str
    folder: str | None = None
    hora: str | None = None
    dias: str | None = None

class BotConfig(BaseModel):
    sunat: SunatConfig
    sap: SapConfig
    general: GeneralConfig
    execution_id: int | None = None

@router.post("/run")
async def run_bot_endpoint(config: BotConfig):
    return await run_bot_logic(config)

async def run_bot_logic(config: BotConfig):
    try:
        current_dir = os.getcwd()
        base_output = os.path.join(current_dir, "output")
        
        # Lógica de carpeta centralizada
        # Sanitizar fecha para nombre de carpeta (reemplazar / por -)
        safe_date = config.general.fecha.replace("/", "-")
        # Obtener hora actual para el nombre de la carpeta (hora de ejecución)
        current_time_str = datetime.now().strftime("%H-%M-%S")
        
        subfolder_name = f"{config.general.sociedad}_{safe_date}_{current_time_str}"
        
        if sys.platform == "win32":
            folder_path = os.path.join(base_output, "windows", subfolder_name)
            os_name = "Windows"
        else:
            folder_path = os.path.join(base_output, "linux", subfolder_name)
            os_name = "Linux"

        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            
        print(f"ℹ️ {os_name} detectado. Carpeta de salida centralizada en: {folder_path}")
        
        # --- NUEVA LÓGICA: ESCRIBIR EN CARPETA DE INTERCAMBIO (WATCHER) ---
        
        # 1. Definir ruta de la carpeta compartida (Exchange)
        # Asumimos que la carpeta 'dmz/exchange/pendientes' es accesible desde el backend
        # En producción, esto debería ser una ruta de red montada o volumen compartido
        
        # Buscamos la carpeta dmz relativa al backend
        # backend/app/api/bot.py -> backend/ -> root/ -> dmz/
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
        # Ajuste de ruta: estamos en backend/app/api, subimos 3 niveles para llegar a backend, uno mas para root
        # Mejor usamos ruta relativa segura
        
        exchange_pending_dir = os.path.join(current_dir, "..", "..", "..", "dmz", "exchange", "pendientes")
        exchange_pending_dir = os.path.abspath(exchange_pending_dir)
        
        if not os.path.exists(exchange_pending_dir):
            # Fallback: intentar ruta absoluta común si no funciona la relativa (ej. desarrollo)
             exchange_pending_dir = r"c:\Users\Soporte\Documents\Proyectos\ocr-cosapi-full\dmz\exchange\pendientes"
             if not os.path.exists(exchange_pending_dir):
                  raise Exception(f"No se encuentra la carpeta de intercambio: {exchange_pending_dir}")

        # 2. Preparar el payload JSON
        # Calculamos los argumentos como antes para mantener compatibilidad con la estructura que espera app.py
        
        month = int(config.general.fecha.split("/")[1])
        year = int(config.general.fecha.split("/")[2])
        
        folder_sap = os.path.join(folder_path, 'sap')
        folder_sunat = os.path.join(folder_path, 'sunat')
        
        job_data = {
            'sap': {
                'code_sociedad': config.general.sociedad,
                'date': config.general.fecha,
                'time': config.general.hora,
                'days': config.general.dias,
                'folder': folder_sap,
                'cred': {
                    'email': config.sap.usuario,
                    'password': config.sap.password
                }
            },
            'sunat': {
                'date': {
                    'month': month,
                    'year': year
                },
                'time': config.general.hora,
                'days': config.general.dias,
                'folder': folder_sunat,
                'cred': {
                    'ruc': config.sunat.ruc,
                    'user': config.sunat.usuario,
                    'clave': config.sunat.claveSol
                },
                'input_date': config.general.fecha
            },
            'socket_url': "http://localhost:8001", # El watcher debe saber a dónde reportar
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # 3. Escribir archivo JSON
        job_id = f"job_{config.general.sociedad}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{config.execution_id or 0}.json"
        job_file_path = os.path.join(exchange_pending_dir, job_id)
        
        import json
        with open(job_file_path, 'w', encoding='utf-8') as f:
            json.dump(job_data, f, indent=4, ensure_ascii=False)
            
        print(f"✅ Trabajo enviado al Watcher: {job_file_path}")
        
        # Simulamos la salida que espera el frontend
        log_lines = [
            f"🚀 Trabajo encolado exitosamente.",
            f"📂 Carpeta de salida: {folder_path}",
            f"📄 ID de Trabajo: {job_id}",
            f"⏳ El servicio DMZ procesará la solicitud en breve."
        ]
        
        return {
             "success": True, 
             "message": "Solicitud enviada al servicio de automatización",
             "job_id": job_id,
             "logs": log_lines
        }

        # --- FIN NUEVA LÓGICA ---
        
    except Exception as e:
        print(f"Error ejecutando bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))
