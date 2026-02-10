import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL")

async def analyze_document_content(file_content: bytes, mime_type: str, prompt: str = None) -> dict:
    """
    Analiza un documento (PDF o Imagen) usando Google Gemini (SDK google-genai).
    """
    if not API_KEY:
        return {"error": "GOOGLE_API_KEY no configurada en el backend (.env)."}
    
    if not MODEL_NAME:
        return {"error": "GEMINI_MODEL no configurada en el backend (.env)."}

    try:
        client = genai.Client(api_key=API_KEY)
        
        if not prompt:
            prompt = "Analiza este documento y extrae toda la información relevante en texto plano."

        response = await client.aio.models.generate_content(
            model=MODEL_NAME,
            contents=[
                types.Part.from_bytes(data=file_content, mime_type=mime_type),
                prompt
            ]
        )
        
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
