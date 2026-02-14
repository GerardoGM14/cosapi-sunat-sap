import time
import os
import json
import shutil
import asyncio
from pathlib import Path
from src.services.gemini_ocr import analyze_first_page_oc, validate_ocr_requirements, analyze_document_content

# Configuración de carpetas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # dmz/gemini-service
DMZ_ROOT = os.path.dirname(BASE_DIR) # dmz
EXCHANGE_DIR = os.path.join(DMZ_ROOT, "exchange", "ocr")

PENDING_DIR = os.path.join(EXCHANGE_DIR, "pendientes")
PROCESSED_DIR = os.path.join(EXCHANGE_DIR, "procesados")
ERROR_DIR = os.path.join(EXCHANGE_DIR, "errores")
FILES_DIR = os.path.join(EXCHANGE_DIR, "files")

# Asegurar que existan
os.makedirs(PENDING_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(ERROR_DIR, exist_ok=True)
os.makedirs(FILES_DIR, exist_ok=True)

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    RESET = '\033[0m'

def log(message, color=Colors.RESET):
    print(f"{color}[GEMINI WATCHER] {message}{Colors.RESET}")

async def process_job(job_file, job_data):
    log(f"🔄 Procesando trabajo OCR: {job_file}", Colors.BLUE)
    
    action = job_data.get('action')
    file_name = job_data.get('file_name')
    
    if not file_name:
        raise Exception("Falta 'file_name' en el trabajo")

    file_path = os.path.join(FILES_DIR, file_name)
    
    if not os.path.exists(file_path):
        raise Exception(f"No se encuentra el archivo: {file_path}")

    result = {}
    
    try:
        if action == 'analyze_first_page_oc':
            log(f"📄 Analizando primera página para O/C: {file_name}", Colors.CYAN)
            result = await analyze_first_page_oc(file_path)
            
        elif action == 'validate_ocr_requirements':
            oc_number = job_data.get('oc_number')
            log(f"🔍 Validando requisitos para O/C {oc_number}: {file_name}", Colors.CYAN)
            result = await validate_ocr_requirements(file_path, oc_number)
            
        elif action == 'analyze_document_content':
             prompt = job_data.get('prompt')
             mime_type = job_data.get('mime_type', 'application/pdf')
             
             # Leer archivo como bytes
             with open(file_path, 'rb') as f:
                 content = f.read()
                 
             log(f"🧠 Analizando contenido completo: {file_name}", Colors.CYAN)
             result = await analyze_document_content(content, mime_type, prompt)
             
        else:
            raise Exception(f"Acción desconocida: {action}")
            
        # Añadir metadatos de éxito
        result['job_status'] = 'completed'
        result['processed_at'] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        return result

    except Exception as e:
        log(f"❌ Error en procesamiento Gemini: {e}", Colors.RED)
        return {"error": str(e), "job_status": "failed"}

def main():
    log(f"👀 Watcher iniciado. Vigilando: {PENDING_DIR}", Colors.CYAN)

    while True:
        try:
            # Listar archivos JSON en pendientes
            files = [f for f in os.listdir(PENDING_DIR) if f.endswith('.json')]
            
            for filename in files:
                file_path = os.path.join(PENDING_DIR, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        job_data = json.load(f)
                    
                    # Ejecutar trabajo
                    result = asyncio.run(process_job(filename, job_data))
                    
                    # Guardar resultado
                    result_filename = filename.replace('.json', '.result.json')
                    result_path = os.path.join(PROCESSED_DIR, result_filename)
                    
                    with open(result_path, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=4, ensure_ascii=False)
                    
                    # Mover trabajo original a procesados (o borrarlo?)
                    # Mejor moverlo para historial
                    shutil.move(file_path, os.path.join(PROCESSED_DIR, filename))
                    
                    if result.get('job_status') == 'completed':
                        log(f"✅ Trabajo completado: {filename}", Colors.GREEN)
                    else:
                        log(f"⚠️ Trabajo completado con error: {filename}", Colors.YELLOW)
                        
                    # Opcional: Eliminar archivo PDF de 'files' si ya no se necesita?
                    # El backend podría necesitarlo o limpiar periódicamente.
                    # Por seguridad, dejémoslo ahí o movámoslo a 'procesados/files'?
                    # Dejémoslo en 'files' por ahora.

                except json.JSONDecodeError:
                    log(f"⚠️ Archivo JSON inválido: {filename}", Colors.RED)
                    shutil.move(file_path, os.path.join(ERROR_DIR, filename))
                except Exception as e:
                    log(f"⚠️ Error procesando archivo {filename}: {e}", Colors.RED)
                    try:
                        shutil.move(file_path, os.path.join(ERROR_DIR, filename))
                    except:
                        pass

            time.sleep(1) # Polling rápido
            
        except KeyboardInterrupt:
            log("\n👋 Watcher detenido por el usuario.", Colors.YELLOW)
            break
        except Exception as e:
            log(f"💥 Error crítico en el loop principal: {e}", Colors.RED)
            time.sleep(5)

if __name__ == "__main__":
    main()
