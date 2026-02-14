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
# Ruta ajustada para DMZ/gemini-service
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
            if response.status_code in [200, 201]:
                print(f"✅ Log de consumo registrado exitosamente en API externa. ID: {API_LOG_GRUPO_ID}")
            else:
                print(f"⚠️ Error registrando consumo en API externa: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ Excepción al enviar log a API externa: {str(e)}")

def clean_oc_value(value: str) -> str:
    """
    Limpia el valor de O/C según las reglas de negocio:
    1. Si empieza con '4', se mantiene (hasta 10 dígitos).
    2. Si no empieza con '4', toma los últimos 10 dígitos (contando de derecha a izquierda).
    """
    if not value:
        return None
        
    # Eliminar caracteres no numéricos para trabajar solo con dígitos
    digits = "".join(filter(str.isdigit, str(value)))
    
    if not digits:
        return None

    # Caso 1: Empieza con 4
    if digits.startswith("4"):
        return digits[:10]
    
    # Caso 2: No empieza con 4 -> Tomar los últimos 10 dígitos
    # Ejemplo: 9994501234567 -> 4501234567
    # Ejemplo: 123 -> 123 (si es menor a 10, toma todo)
    if len(digits) > 10:
        return digits[-10:]
    else:
        return digits

def classify_document(oc_value: str) -> dict:
    """
    Clasifica el documento según el rango numérico del O/C.
    Retorna un diccionario con 'clase_documento' y 'denominacion'.
    Maneja superposiciones de rangos concatenando las opciones con ' / '.
    """
    if not oc_value or not oc_value.isdigit():
        return {"clase_documento": None, "denominacion": None}
    
    try:
        oc_num = int(oc_value)
    except ValueError:
        return {"clase_documento": None, "denominacion": None}

    clases = []
    denominaciones = []

    # ZBNS: 4000000000 - 4099999999
    if 4000000000 <= oc_num <= 4099999999:
        clases.append("ZBNS")
        denominaciones.append("OC Nacional c/Solic.")

    # ZBNC: 4000000000 - 4099999999
    if 4000000000 <= oc_num <= 4099999999:
        clases.append("ZBNC")
        denominaciones.append("OC Nacional c/Contr.")

    # ZIMP: 4100000000 - 4199999999
    if 4100000000 <= oc_num <= 4199999999:
        clases.append("ZIMP")
        denominaciones.append("OC Import. c/Solic.")
        
    # ZSUB: 4200000000 - 4299999999
    if 4200000000 <= oc_num <= 4299999999:
        clases.append("ZSUB")
        denominaciones.append("OC Subcont. c/Solic.")
        
    # ZSES: 4300000000 - 4499999999
    if 4300000000 <= oc_num <= 4499999999:
        clases.append("ZSES")
        denominaciones.append("OC Servicios c/Solic.")

    # ZSEC: 4300000000 - 4499999999
    if 4300000000 <= oc_num <= 4499999999:
        clases.append("ZSEC")
        denominaciones.append("OC Servicios c/Cont.")
        
    # ZTM1: 4400000000 - 4499999999
    if 4400000000 <= oc_num <= 4499999999:
        clases.append("ZTM1")
        denominaciones.append("OC Serv. Transp.")
        
    # ZCON: 4500000000 - 4599999999
    if 4500000000 <= oc_num <= 4599999999:
        clases.append("ZCON")
        denominaciones.append("Ord. Consignación")
        
    # ZAFL: 4600000000 - 4699999999
    if 4600000000 <= oc_num <= 4699999999:
        clases.append("ZAFL")
        denominaciones.append("OC Afijo Nac. c/Solic.")

    # ZAFI: 4600000000 - 4699999999
    if 4600000000 <= oc_num <= 4699999999:
        clases.append("ZAFI")
        denominaciones.append("OC Afijo Import. c/Solic.")
        
    if not clases:
        return {"clase_documento": "DESCONOCIDO", "denominacion": "Rango no clasificado"}

    # Eliminar duplicados si fuera necesario, aunque aquí los ifs son explícitos
    # Formatear salida
    return {
        "clase_documento": " / ".join(clases),
        "denominacion": " / ".join(denominaciones)
    }

async def validate_ocr_requirements(file_path: str, oc_number: str) -> dict:
    """
    Valida los requisitos documentarios según el prefijo del O/C.
    Lee todo el PDF y usa Gemini para buscar documentos obligatorios.
    """
    if not oc_number:
        return {"validation_status": "skipped", "reason": "No O/C number provided"}
        
    prefix = oc_number[:2]
    
    requirements_prompt = ""
    if prefix == "43":
        requirements_prompt = """
        TIPO: ORDEN DE SERVICIO (Prefijo 43...)
        DOCUMENTOS OBLIGATORIOS:
        1. Factura
        2. HES (Hoja de Entrada de Servicios)
        3. Orden de Servicio completa
        
        DOCUMENTOS OPCIONALES:
        - Valorización
        
        REGLA DE VALIDACIÓN DE FIRMAS:
        - Si detectas una 'Valorización', verifica si tiene firmas (manuscritas o digitales).
        """
    elif prefix == "40":
        requirements_prompt = """
        TIPO: ORDEN DE COMPRA (Prefijo 40...)
        DOCUMENTOS OBLIGATORIOS:
        1. Factura
        2. Guías de remisión
        3. HEM (Hoja de Entrada de Materiales)
        4. Orden de Compra completa
        """
    elif prefix == "42":
        requirements_prompt = """
        TIPO: ORDEN DE SUBCONTRATO (Prefijo 42...)
        DOCUMENTOS OBLIGATORIOS:
        1. Factura
        2. Valorización
        3. HES (Hoja de Entrada de Servicios)
        4. Orden de Subcontrato completa
        """
    else:
        return {"validation_status": "skipped", "reason": "No validation rules for O/C prefix " + prefix}

    print(f"🔍 Validando requisitos para O/C {oc_number} ({prefix}) en {file_path}")

    try:
        # Leer todo el PDF
        with open(file_path, "rb") as f:
            file_content = f.read()
            
        client = genai.Client(api_key=API_KEY)
        
        prompt = f"""
        Analiza este documento PDF completo.
        Tu tarea es validar si el paquete de documentos cumple con los requisitos para una {requirements_prompt.splitlines()[1].strip()}.
        
        {requirements_prompt}
        
        Devuelve un JSON ESTRICTO con la siguiente estructura:
        {{
            "present_documents": ["Lista", "de", "documentos", "encontrados"],
            "missing_documents": ["Lista", "de", "documentos", "obligatorios", "faltantes"],
            "valorizacion_detected": true/false,
            "valorizacion_signed": true/false/null, (null si no hay valorización, true si tiene firmas, false si no)
            "is_compliant": true/false, (true solo si están TODOS los obligatorios)
            "observations": "Texto breve describiendo hallazgos o problemas (ej. falta firma en valorización)"
        }}
        NO uses markdown. Solo JSON.
        """

        response = await client.aio.models.generate_content(
            model=MODEL_NAME or "gemini-2.0-flash",
            contents=[
                types.Content(
                    parts=[
                        types.Part.from_bytes(data=file_content, mime_type="application/pdf"),
                        types.Part.from_text(text=prompt)
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        if response.text:
            try:
                validation_result = json.loads(response.text.replace("```json", "").replace("```", "").strip())
                return {"validation_status": "performed", "result": validation_result}
            except json.JSONDecodeError:
                return {"validation_status": "error", "error": "Invalid JSON from Gemini validation"}
                
        return {"validation_status": "error", "error": "No response text from Gemini validation"}

    except Exception as e:
        print(f"⚠️ Error en validate_ocr_requirements: {e}")
        return {"validation_status": "error", "error": str(e)}

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
            
            # Aplicar limpieza de O/C
            if result_json.get("O/C"):
                raw_oc = result_json["O/C"]
                cleaned_oc = clean_oc_value(raw_oc)
                result_json["O/C"] = cleaned_oc
                result_json["O/C_Original"] = raw_oc # Guardamos el original para debug
                
                # Clasificar documento basado en O/C limpio
                classification = classify_document(cleaned_oc)
                result_json.update(classification)
            else:
                result_json["clase_documento"] = None
                result_json["denominacion"] = None
                
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

        response = await client.aio.models.generate_content(
            model=MODEL_NAME,
            contents=[
                types.Part.from_bytes(data=file_content, mime_type=mime_type),
                prompt
            ]
        )

        usage = response.usage_metadata
        t_in = usage.prompt_token_count if usage else 0
        t_out = usage.candidates_token_count if usage else 0
        
        is_pdf = "pdf" in mime_type.lower()
        pages = count_pdf_pages(file_content) if is_pdf else 1

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
