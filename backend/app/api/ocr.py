from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.gemini_ocr import analyze_document_content, analyze_first_page_oc
from typing import Optional
import shutil
import os
import uuid

router = APIRouter()

# Directorio temporal para PDFs
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
PDF_DIR = os.path.join(BASE_DIR, "app", "pdf")

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
