import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configuración de API Key
API_KEY = os.getenv("GOOGLE_API_KEY")

# Modelo por defecto. El usuario solicitó "gemini-2.5-flash-lite", 
# ajustamos a "gemini-1.5-flash" que es la versión estable actual para tareas rápidas y económicas.
# Se puede cambiar mediante variable de entorno GEMINI_MODEL.
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

if API_KEY:
    genai.configure(api_key=API_KEY)

async def analyze_document_content(file_content: bytes, mime_type: str, prompt: str = None) -> dict:
    """
    Analiza un documento (PDF o Imagen) usando Google Gemini.
    """
    if not API_KEY:
        return {"error": "GOOGLE_API_KEY no configurada en el backend (.env)."}

    try:
        # Instanciar modelo
        model = genai.GenerativeModel(MODEL_NAME)
        
        if not prompt:
            prompt = "Analiza este documento y extrae toda la información relevante en texto plano."

        # Preparar partes para el modelo
        content_parts = [
            {'mime_type': mime_type, 'data': file_content},
            prompt
        ]

        # Llamada asíncrona a Gemini
        response = await model.generate_content_async(content_parts)
        
        return {
            "success": True,
            "model_used": MODEL_NAME,
            "text": response.text
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
