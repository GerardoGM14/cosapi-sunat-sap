from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.gemini_ocr import analyze_document_content
from typing import Optional

router = APIRouter()

@router.post("/scan", summary="Analizar documento con Gemini OCR")
async def scan_document(
    file: UploadFile = File(...),
    prompt: Optional[str] = Form("Analiza este documento y extrae la información clave.")
):
    """
    Sube un archivo (PDF o Imagen) y procésalo con Gemini Flash.
    """
    # Validar tipos MIME soportados por Gemini
    allowed_types = [
        "application/pdf", 
        "image/jpeg", 
        "image/png", 
        "image/webp", 
        "image/heic", 
        "image/heif"
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Tipo de archivo no soportado ({file.content_type}). Use PDF o imágenes."
        )
    
    # Leer contenido
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error leyendo archivo: {str(e)}")
        
    # Procesar con servicio Gemini
    result = await analyze_document_content(content, file.content_type, prompt)
    
    if "error" in result and result.get("error"):
        # Si es un error de configuración (API Key), devolvemos 500
        if "GOOGLE_API_KEY" in result["error"]:
            raise HTTPException(status_code=500, detail=result["error"])
        # Otros errores de procesamiento
        raise HTTPException(status_code=500, detail=f"Error en Gemini: {result['error']}")
        
    return result
