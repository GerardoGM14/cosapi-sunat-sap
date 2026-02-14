import os
import time
import json
import shutil
import uuid
import asyncio

# Configuración de carpetas DMZ
# backend/app/services/gemini_ocr.py -> backend/app/services -> backend/app -> backend -> root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DMZ_DIR = os.path.join(ROOT_DIR, "dmz")
EXCHANGE_DIR = os.path.join(DMZ_DIR, "exchange", "ocr")

PENDING_DIR = os.path.join(EXCHANGE_DIR, "pendientes")
PROCESSED_DIR = os.path.join(EXCHANGE_DIR, "procesados")
ERROR_DIR = os.path.join(EXCHANGE_DIR, "errores")
FILES_DIR = os.path.join(EXCHANGE_DIR, "files")

# Asegurar que existan (por si acaso el backend corre antes que el setup de carpetas, aunque ya las creamos)
os.makedirs(PENDING_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(ERROR_DIR, exist_ok=True)
os.makedirs(FILES_DIR, exist_ok=True)

def _generate_job_id():
    return str(uuid.uuid4())

async def _submit_and_wait(action: str, file_path: str = None, file_content: bytes = None, file_ext: str = ".pdf", **kwargs):
    """
    Envía un trabajo a la DMZ y espera el resultado.
    """
    job_id = _generate_job_id()
    job_filename = f"{job_id}.json"
    result_filename = f"{job_id}.result.json"
    
    # 1. Preparar archivo
    target_file_name = f"{job_id}{file_ext}"
    target_file_path = os.path.join(FILES_DIR, target_file_name)
    
    try:
        if file_path:
            shutil.copy(file_path, target_file_path)
        elif file_content:
            with open(target_file_path, "wb") as f:
                f.write(file_content)
        else:
            raise ValueError("Se requiere file_path o file_content")
    except Exception as e:
        return {"error": f"Error copiando archivo a DMZ: {str(e)}"}
        
    # 2. Crear Job JSON
    job_data = {
        "job_id": job_id,
        "action": action,
        "file_name": target_file_name,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        **kwargs
    }
    
    job_path = os.path.join(PENDING_DIR, job_filename)
    with open(job_path, "w", encoding="utf-8") as f:
        json.dump(job_data, f, indent=4, ensure_ascii=False)
        
    # 3. Esperar resultado (Polling)
    # Timeout de 60 segundos por defecto (Gemini puede tardar)
    timeout = 120 
    start_time = time.time()
    
    result_path = os.path.join(PROCESSED_DIR, result_filename)
    
    while time.time() - start_time < timeout:
        if os.path.exists(result_path):
            # Leer resultado
            try:
                # Pequeña espera para asegurar escritura completa
                await asyncio.sleep(0.1) 
                with open(result_path, "r", encoding="utf-8") as f:
                    result = json.load(f)
                
                # Limpieza opcional (el watcher ya mueve el job, pero el result queda)
                # Podríamos borrar el result y el archivo de files para ahorrar espacio
                try:
                    os.remove(result_path)
                    # os.remove(target_file_path) # Dejar archivo por si acaso se necesita depurar
                except:
                    pass
                    
                return result
            except Exception as e:
                return {"error": f"Error leyendo resultado de DMZ: {str(e)}"}
        
        await asyncio.sleep(0.5)
        
    return {"error": "Timeout esperando respuesta de DMZ Gemini Service"}

# Funciones públicas que imitan la interfaz original

async def analyze_first_page_oc(file_path: str) -> dict:
    """
    Proxy para analyze_first_page_oc en DMZ.
    """
    return await _submit_and_wait("analyze_first_page_oc", file_path=file_path)

async def validate_ocr_requirements(file_path: str, oc_number: str) -> dict:
    """
    Proxy para validate_ocr_requirements en DMZ.
    """
    return await _submit_and_wait("validate_ocr_requirements", file_path=file_path, oc_number=oc_number)

async def analyze_document_content(file_content: bytes, mime_type: str, prompt: str = None) -> dict:
    """
    Proxy para analyze_document_content en DMZ.
    """
    ext = ".pdf"
    if "image" in mime_type:
        ext = ".jpg" # O inferir extensión
        
    return await _submit_and_wait(
        "analyze_document_content", 
        file_content=file_content, 
        file_ext=ext,
        mime_type=mime_type, 
        prompt=prompt
    )

# Funciones auxiliares que ya no se usan en backend pero se mantienen por compatibilidad si algo las importa
def count_pdf_pages(file_content: bytes) -> int:
    return 0 

async def send_log_background(*args, **kwargs):
    pass
