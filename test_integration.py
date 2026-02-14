import asyncio
import os
import sys
import json
import time

# Agregar backend al path para poder importar módulos
sys.path.append(os.path.abspath("backend"))

from app.services.gemini_ocr import analyze_first_page_oc

async def test_ocr_flow():
    print("\n--- 🚀 PRUEBA 1: FLUJO OCR (Backend -> DMZ -> Backend) ---")
    
    # 1. Crear un archivo dummy que simule ser un PDF
    dummy_file_path = "temp_dummy_test.pdf"
    with open(dummy_file_path, "wb") as f:
        f.write(b"%PDF-1.4 header dummy content")
    
    try:
        print(f"📤 Enviando trabajo OCR desde {dummy_file_path}...")
        # Llamamos a la función del backend que ahora actúa como proxy
        # Esta función escribe en dmz/exchange/ocr/pendientes y espera respuesta
        result = await analyze_first_page_oc(
            file_path=os.path.abspath(dummy_file_path)
        )
        
        print("\n✅ RESPUESTA RECIBIDA DEL WATCHER OCR:")
        print(result)
        
        if "error" in result:
            print("\n⚠️ Nota: Recibimos un error, lo cual es ESPERADO porque enviamos un PDF falso.")
            print("   Lo importante es que el error vino del Watcher, confirmando la comunicación.")
        else:
            print("\n🎉 ¡Éxito total! Se procesó correctamente.")
            
    except Exception as e:
        print(f"\n❌ Error en la prueba OCR: {e}")
    finally:
        if os.path.exists(dummy_file_path):
            os.remove(dummy_file_path)

async def test_sap_flow():
    print("\n--- 🚀 PRUEBA 2: FLUJO SAP/SUNAT (Backend -> DMZ -> Ejecución) ---")
    
    # Rutas
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dmz_dir = os.path.join(script_dir, "dmz")
    exchange_dir = os.path.join(dmz_dir, "exchange")
    pending_dir = os.path.join(exchange_dir, "pendientes")
    processed_dir = os.path.join(exchange_dir, "procesados")
    error_dir = os.path.join(exchange_dir, "errores")
    
    # 1. Crear Job JSON simulado
    job_id = "test_sap_integration_" + str(int(time.time()))
    job_filename = f"{job_id}.json"
    job_path = os.path.join(pending_dir, job_filename)
    
    job_data = {
        "job_id": job_id,
        "sap": {
            "dummy_param": "test",
            "code_sociedad": "1000",
            "date": "2023/10/01"
        }
    }
    
    print(f"📤 Creando trabajo SAP simulado en: {job_path}")
    with open(job_path, "w", encoding="utf-8") as f:
        json.dump(job_data, f, indent=4)
        
    # 2. Esperar a que el watcher lo mueva
    print("⏳ Esperando que el Watcher SAP procese el archivo...")
    timeout = 15
    start_time = time.time()
    
    status = "timeout"
    
    while time.time() - start_time < timeout:
        if not os.path.exists(job_path):
            # El archivo desapareció de pendientes, buscar en procesados o errores
            if os.path.exists(os.path.join(processed_dir, job_filename)):
                status = "processed"
                break
            elif os.path.exists(os.path.join(error_dir, job_filename)):
                status = "error" # Probablemente falle por argumentos dummy, pero eso es éxito de comunicación
                break
        await asyncio.sleep(1)
        
    if status == "processed":
        print(f"\n✅ ¡ÉXITO! El trabajo fue procesado y movido a {processed_dir}")
    elif status == "error":
        print(f"\n✅ ¡ÉXITO! El trabajo fue procesado (con error esperado) y movido a {error_dir}")
        print("   (El error es esperado porque enviamos parámetros dummy, pero confirma que el Watcher actuó)")
    else:
        print(f"\n❌ FALLO: El archivo sigue en {pending_dir} o desapareció sin rastro.")

async def main():
    await test_ocr_flow()
    await test_sap_flow()

if __name__ == "__main__":
    asyncio.run(main())
