import os
import io
import json
import asyncio
import httpx
from pypdf import PdfReader, PdfWriter
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Configuración de API Key
API_KEY = os.getenv("GOOGLE_API_KEY")

# Modelo por defecto.
MODEL_NAME = os.getenv("GEMINI_MODEL")

# Cargar configuración desde consumer_config.json
CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "consumer_config.json")

def load_consumer_config():
    if not os.path.exists(CONFIG_FILE_PATH):
        print(f"⚠️ Archivo de configuración {CONFIG_FILE_PATH} no encontrado.")
        return {}
    try:
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Error leyendo {CONFIG_FILE_PATH}: {e}")
        return {}

consumer_config = load_consumer_config()

# Configuración API Logs (desde JSON)
API_LOG_URL = consumer_config.get("api_url")
API_LOG_GRUPO_ID = consumer_config.get("grupo_id", 1)
API_LOG_SERVICIO_ID = consumer_config.get("servicio_id", 2)
API_LOG_ORIGEN = consumer_config.get("origen", "WebApp")
API_LOG_PROYECTO = consumer_config.get("proyecto", "AnalizadorFinanciero")
API_LOG_EMPRESA = consumer_config.get("empresa", "Empresa S.A. de C.V.")
API_LOG_IP = consumer_config.get("ip_publica", "127.0.0.1")
API_LOG_KEY = consumer_config.get("api_key")

def count_pdf_pages(file_content: bytes) -> int:
    try:
        reader = PdfReader(io.BytesIO(file_content))
        return len(reader.pages)
    except Exception:
        return 1 # Fallback si falla lectura o no es PDF válido

async def send_log_background(
    tokens_in: int, 
    tokens_out: int, 
    pages: int, 
    is_image: bool,
    model_used: str
):
    """
    Envía el registro de consumo a la API externa en segundo plano.
    No bloquea ni interrumpe el flujo principal si falla.
    """
    if not API_LOG_URL:
        print("⚠️ API_LOG_URL no configurada en consumer_config.json, saltando registro de consumo.")
        return

    payload = {
        "grupoId": API_LOG_GRUPO_ID,
        "servicioId": API_LOG_SERVICIO_ID,
        "tokensIn": tokens_in,
        "tokensOut": tokens_out,
        "numeroLlamados": 1,
        "observaciones": f"Proceso de análisis completado con {model_used}",
        "cantidadArchivos": 1,
        "cantidadPaginas": pages,
        "cantidadImagenes": 1 if is_image else 0,
        "origen": API_LOG_ORIGEN,
        "proyecto": API_LOG_PROYECTO,
        "versionIA": model_used,
        "ipPublica": API_LOG_IP,
        "empresa": API_LOG_EMPRESA,
        # Campos redundantes requeridos por la API (según ejemplo usuario)
        "cantidadFoliosLocal": pages,
        "cantidadArchivosLocal": 1,
        "cantidadFoliosProcesados": pages,
        "cantidadArchivosProcesados": 1
    }

    try:
        headers = {}
        if API_LOG_KEY:
            headers["x-api-key"] = API_LOG_KEY

        async with httpx.AsyncClient() as client:
            response = await client.post(API_LOG_URL, json=payload, headers=headers, timeout=5.0)
            if response.status_code == 200:
                print(f"✅ Log de consumo registrado exitosamente en API externa. ID: {API_LOG_GRUPO_ID}")
            else:
                print(f"⚠️ Error registrando consumo en API externa: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ Excepción al enviar log a API externa: {str(e)}")

async def analyze_first_page_oc(file_path: str) -> dict:
    """
    Analiza solo la primera página del PDF para encontrar el O/C.
    Guarda temporalmente la primera página en memoria y la envía a Gemini.
    """
    try:
        # 1. Extraer primera página
        reader = PdfReader(file_path)
        if len(reader.pages) < 1:
            return {"error": "El PDF está vacío"}
            
        writer = PdfWriter()
        writer.add_page(reader.pages[0])
        
        first_page_stream = io.BytesIO()
        writer.write(first_page_stream)
        first_page_content = first_page_stream.getvalue()
        
        # 2. Preparar cliente Gemini
        client = genai.Client(api_key=API_KEY)
        
        prompt = """
        Analiza esta imagen/documento (que es la primera página de un archivo).
        Tu ÚNICA tarea es encontrar el número de Orden de Compra, que suele aparecer como:
        - "O/C"
        - "O/C CLIENTE"
        - "Orden de Compra"
        - "Purchase Order"
        - "PO"
        
        Devuelve la respuesta ESTRICTAMENTE en formato JSON:
        {
            "O/C": "valor_encontrado"
        }
        
        Si no encuentras ningún código con ese formato, devuelve:
        {
            "O/C": null
        }
        NO añadas bloques de código markdown (```json), solo el texto JSON puro.
        """
               
        response = client.models.generate_content(
            model=MODEL_NAME or "gemini-2.0-flash", # Fallback si no hay modelo en env
            contents=[
                types.Content(
                    parts=[
                        types.Part.from_bytes(data=first_page_content, mime_type="application/pdf"),
                        types.Part.from_text(text=prompt)
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        # 4. Procesar respuesta
        if response.text:
            try:
                result_json = json.loads(response.text)
            except json.JSONDecodeError:
                # Intento de limpieza si gemini manda markdown
                clean_text = response.text.replace("```json", "").replace("```", "").strip()
                result_json = json.loads(clean_text)
                
            # Calcular tokens para el log (estimado o real si la respuesta lo trae)
            usage = response.usage_metadata
            tokens_in = usage.prompt_token_count if usage else 0
            tokens_out = usage.candidates_token_count if usage else 0
            
            # Enviar log en background
            asyncio.create_task(send_log_background(
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                pages=len(reader.pages), # Total páginas del doc original
                is_image=False,
                model_used=MODEL_NAME or "gemini-fallback"
            ))
            
            return result_json
        
        return {"O/C": None, "error": "No response text"}

    except Exception as e:
        print(f"Error en analyze_first_page_oc: {e}")
        return {"error": str(e)}

async def analyze_document_content(file_content: bytes, mime_type: str, prompt: str = None) -> dict:
    """
    Analiza un documento (PDF o Imagen) usando Google Gemini (SDK google-genai).
    """
    if not API_KEY:
        return {"error": "GOOGLE_API_KEY no configurada en el backend (.env)."}
    
    if not MODEL_NAME:
        return {"error": "GEMINI_MODEL no configurada en el backend (.env)."}

    try:
        # Instanciar cliente
        client = genai.Client(api_key=API_KEY)
        
        if not prompt:
            prompt = "Analiza este documento y extrae toda la información relevante en texto plano."

        # Preparar contenido. 
        # El nuevo SDK acepta bytes directamente en types.Part.from_bytes
        # o una lista mixta en contents.
        
        # Llamada asíncrona a Gemini
        # Usamos client.aio para métodos asíncronos
        response = await client.aio.models.generate_content(
            model=MODEL_NAME,
            contents=[
                types.Part.from_bytes(data=file_content, mime_type=mime_type),
                prompt
            ]
        )
        
        # Cálculo de métricas para el log
        usage = response.usage_metadata
        t_in = usage.prompt_token_count if usage else 0
        t_out = usage.candidates_token_count if usage else 0
        
        is_pdf = "pdf" in mime_type.lower()
        pages = count_pdf_pages(file_content) if is_pdf else 1
        
        # Enviar log en background (Fire and forget)
        asyncio.create_task(send_log_background(
            tokens_in=t_in,
            tokens_out=t_out,
            pages=pages,
            is_image=not is_pdf,
            model_used=MODEL_NAME
        ))

        return {
            "success": True,
            "model_used": MODEL_NAME,
            "text": response.text,
            "usage": {
                "prompt_tokens": t_in,
                "response_tokens": t_out
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
