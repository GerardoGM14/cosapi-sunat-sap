from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Body
from app.services.gemini_ocr import analyze_document_content, analyze_first_page_oc, validate_ocr_requirements
from typing import Optional, List
import shutil
import os
import uuid
import asyncio
from datetime import datetime
from pydantic import BaseModel
from app.socket_manager import sio, EmitEvent

router = APIRouter()

# Directorio temporal para PDFs
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
PDF_DIR = os.path.join(BASE_DIR, "app", "pdf")

class BatchProcessRequest(BaseModel):
    folders: List[str] # Lista de rutas de carpetas a procesar
    concurrency: int = 5 # Nivel de concurrencia (default 5)

@router.post("/scan-batch", summary="Procesar múltiples carpetas de PDFs en paralelo")
async def scan_batch_folders(payload: BatchProcessRequest):
    """
    Escanea recursivamente las carpetas dadas en busca de archivos .pdf
    y los procesa en paralelo usando asyncio y un semáforo.
    Reporta progreso vía Socket.IO.
    """
    all_pdf_files = []
    
    # 1. Recolectar todos los PDFs
    for folder in payload.folders:
        if not os.path.exists(folder):
            print(f"⚠️ Carpeta no encontrada: {folder}")
            continue
            
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.lower().endswith(".pdf"):
                    # Normalizar ruta para usar siempre '/' y evitar mezclas en Windows
                    full_path = os.path.join(root, file).replace("\\", "/")
                    all_pdf_files.append(full_path)
    
    total_files = len(all_pdf_files)
    if total_files == 0:
        return {"message": "No se encontraron archivos PDF en las rutas proporcionadas", "total": 0}

    print(f"🚀 Iniciando procesamiento batch de {total_files} archivos con concurrencia {payload.concurrency}")
    
    # Notificar inicio
    await sio.emit(EmitEvent.LOG, {
        "type": "batch_start",
        "total": total_files,
        "message": f"Iniciando procesamiento de {total_files} archivos..."
    })

    # 2. Configurar Semáforo para controlar concurrencia
    semaphore = asyncio.Semaphore(payload.concurrency)
    results = []
    processed_count = 0

    async def process_single_pdf(file_path):
        nonlocal processed_count
        async with semaphore:
            try:
                # Procesar archivo
                ocr_result = await analyze_first_page_oc(file_path)
                
                status = "success"
                oc_value = ocr_result.get("O/C")
                clase_doc = ocr_result.get("clase_documento")
                denominacion = ocr_result.get("denominacion")
                error = ocr_result.get("error")
                
                if error:
                    status = "error"
                
                # Validación de requisitos documentarios si hay O/C
                validation_result = None
                if oc_value and status == "success":
                    # Emitir log de inicio de validación
                    await sio.emit(EmitEvent.LOG, {
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "message": f"🔍 Validando requisitos para {os.path.basename(file_path)} (O/C: {oc_value})..."
                    })

                    try:
                        validation_result = await validate_ocr_requirements(file_path, oc_value)
                        
                        # Preparar mensaje de resultado para log
                        if validation_result.get("validation_status") == "performed":
                            res = validation_result.get("result", {})
                            is_compliant = res.get("is_compliant", False)
                            missing = res.get("missing_documents", [])
                            obs = res.get("observations", "")
                            
                            status_icon = "✅" if is_compliant else "❌"
                            msg_parts = [f"Validación {status_icon}"]
                            
                            if not is_compliant:
                                msg_parts.append("No cumple requisitos")
                                if missing:
                                    msg_parts.append(f"Faltan: {', '.join(missing)}")
                            else:
                                msg_parts.append("Cumple requisitos")
                                
                            if obs:
                                msg_parts.append(f"Obs: {obs}")
                                
                            log_message = " - ".join(msg_parts)
                        elif validation_result.get("validation_status") == "skipped":
                            log_message = f"Validación omitida: {validation_result.get('reason')}"
                        else:
                            log_message = "Resultado de validación desconocido"

                        await sio.emit(EmitEvent.LOG, {
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "message": f"📄 {os.path.basename(file_path)}: {log_message}"
                        })

                    except Exception as val_e:
                        print(f"Error en validación para {file_path}: {val_e}")
                        validation_result = {"validation_status": "error", "error": str(val_e)}
                        
                        await sio.emit(EmitEvent.LOG, {
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "message": f"⚠️ Error validando {os.path.basename(file_path)}: {val_e}"
                        })

                result_data = {
                    "file_path": file_path,
                    "file_name": os.path.basename(file_path),
                    "status": status,
                    "oc": oc_value,
                    "clase_documento": clase_doc,
                    "denominacion": denominacion,
                    "validation": validation_result,
                    "error": error
                }
                
                # Actualizar contador
                processed_count += 1
                
                # Emitir progreso individual
                await sio.emit(EmitEvent.LOG, {
                    "type": "batch_progress",
                    "current": processed_count,
                    "total": total_files,
                    "file": os.path.basename(file_path),
                    "result": result_data,
                    # Compatibilidad con visor de logs genérico
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "message": f"Procesado {os.path.basename(file_path)}: {status}"
                })
                
                return result_data
                
            except Exception as e:
                print(f"Error procesando {file_path}: {e}")
                processed_count += 1
                return {
                    "file_path": file_path, 
                    "status": "error", 
                    "error": str(e)
                }

    # 3. Crear tareas y ejecutar
    tasks = [process_single_pdf(pdf) for pdf in all_pdf_files]
    results = await asyncio.gather(*tasks)
    
    # 4. Resumen final
    success_count = sum(1 for r in results if r["status"] == "success")
    error_count = total_files - success_count
    
    summary = {
        "total": total_files,
        "success": success_count,
        "errors": error_count,
        "details": results
    }
    
    await sio.emit(EmitEvent.LOG, {
        "type": "batch_complete",
        "summary": summary,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": f"Proceso batch completado. Éxitos: {success_count}, Errores: {error_count}"
    })
    
    return summary

@router.post("/scan", summary="Analizar documento con Gemini OCR")
async def scan_document(
    file: UploadFile = File(...),
    prompt: Optional[str] = Form(None) # Prompt opcional, aunque ahora usamos uno fijo para O/C
):
    """
    Sube un archivo PDF, lo guarda temporalmente y extrae el O/C de la primera página.
    """
    # Validar tipos MIME soportados
    allowed_types = ["application/pdf"]
    
    if file.content_type not in allowed_types:
        # Fallback para imágenes si se desea mantener compatibilidad antigua, 
        # pero el requerimiento específico fue PDF y O/C.
        # Si envían imagen, podríamos procesarla también, pero la lógica de "primera página" cambia.
        # Por ahora restringimos a PDF como pidió el usuario para esta lógica.
        if file.content_type.startswith("image/"):
             # Mantener lógica antigua para imágenes si es necesario, 
             # pero el usuario enfatizó "mis PDF".
             # Vamos a permitir imágenes pero sin guardado en carpeta PDF específico si no es PDF?
             # Mejor simplificamos: Si es imagen, error por ahora o paso directo.
             pass
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Tipo de archivo no soportado ({file.content_type}). Solo PDF."
            )
    
    # Asegurar directorio
    os.makedirs(PDF_DIR, exist_ok=True)
    
    # Generar nombre único para evitar colisiones
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(PDF_DIR, unique_filename)
    
    # Guardar archivo
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando archivo: {str(e)}")
        
    # Procesar con servicio Gemini (O/C en primera página)
    result = await analyze_first_page_oc(file_path)
    
    # Opcional: Eliminar archivo después del proceso? 
    # El usuario dijo "esta ubicación es temporal porque despues yo lo voy a traer en automático"
    # No dijo explícitamente borrarlo YA. Lo dejaré ahí por ahora.
    
    if "error" in result and result.get("error"):
        # Si es un error de configuración (API Key), devolvemos 500
        if result["error"] and "GOOGLE_API_KEY" in str(result["error"]):
            raise HTTPException(status_code=500, detail=result["error"])
        # Otros errores de procesamiento
        raise HTTPException(status_code=500, detail=f"Error en Gemini: {result['error']}")
        
    return result
