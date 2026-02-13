from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess
import sys
import os
import asyncio
import threading
from datetime import datetime
from app.socket_manager import sio
from app.database import SessionLocal
from app.models import DSeguimiento

router = APIRouter()

class SunatConfig(BaseModel):
    ruc: str
    usuario: str
    claveSol: str

class SapConfig(BaseModel):
    usuario: str
    password: str

class GeneralConfig(BaseModel):
    sociedad: str
    fecha: str
    folder: str | None = None
    hora: str | None = None
    dias: str | None = None

class BotConfig(BaseModel):
    sunat: SunatConfig
    sap: SapConfig
    general: GeneralConfig
    execution_id: int | None = None

@router.post("/run")
async def run_bot_endpoint(config: BotConfig):
    return await run_bot_logic(config)

async def run_bot_logic(config: BotConfig):
    try:
        current_dir = os.getcwd()
        base_output = os.path.join(current_dir, "output")
        
        # Lógica de carpeta centralizada
        if sys.platform == "win32":
            folder_path = os.path.join(base_output, "windows")
            os_name = "Windows"
        else:
            folder_path = os.path.join(base_output, "linux")
            os_name = "Linux"

        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            
        print(f"ℹ️ {os_name} detectado. Carpeta de salida centralizada en: {folder_path}")
        possible_service_dir = os.path.abspath(os.path.join(current_dir, "..", "sunat-sap-service"))
        
        if not os.path.exists(possible_service_dir):
             possible_service_dir = os.path.abspath(os.path.join(current_dir, "sunat-sap-service"))
        
        service_dir = possible_service_dir
        script_path = os.path.join(service_dir, "app.py")
        
        if not os.path.exists(script_path):
             if sys.platform == "win32":
                script_path = r"c:\Users\Soporte\Documents\Proyectos\ocr-cosapi-full\sunat-sap-service\app.py"
             else:
                script_path = os.path.join(os.getcwd(), "sunat-sap-service", "app.py")
                if not os.path.exists(script_path):
                     script_path = "/opt/ocr-cosapi-full/sunat-sap-service/app.py"

             service_dir = os.path.dirname(script_path)
        python_executable = sys.executable
        
        if sys.platform == "win32":
            possible_service_venv = os.path.join(service_dir, ".venv", "Scripts", "python.exe")
        else:
            possible_service_venv = os.path.join(service_dir, ".venv", "bin", "python")

        if os.path.exists(possible_service_venv):
            python_executable = possible_service_venv

        env = os.environ.copy()
        env["CONFIG_METHOD"] = "console"
        env["PYTHONPATH"] = service_dir
        env["HEADLESS"] = "false"
        env["PYTHONUNBUFFERED"] = "1"

        if sys.platform == "linux":
            if not env.get("DISPLAY"):
                env_file_path = os.path.join(service_dir, ".env")
                display_from_env = None
                if os.path.exists(env_file_path):
                    try:
                        with open(env_file_path, "r") as f:
                            for line in f:
                                if line.strip().startswith("DISPLAY="):
                                    display_from_env = line.strip().split("=", 1)[1].strip()
                                    break
                    except:
                        pass
                
                if display_from_env:
                    env["DISPLAY"] = display_from_env
                    print(f"ℹ️ Usando DISPLAY desde .env: {display_from_env}")
                else:
                    print("⚠️ Variable DISPLAY no encontrada o vacía. Asignando DISPLAY=:1 (predeterminado para este servidor)")
                    env["DISPLAY"] = ":1"

                home_dir = os.path.expanduser("~")
                xauth_path = os.path.join(home_dir, ".Xauthority")
                
                if os.path.exists(xauth_path):
                    env["XAUTHORITY"] = xauth_path
                    print(f"ℹ️ Usando XAUTHORITY: {xauth_path}")
                else:
                    possible_xauth = "/home/sertech/.Xauthority"
                    if os.path.exists(possible_xauth):
                         env["XAUTHORITY"] = possible_xauth
                         print(f"ℹ️ Usando XAUTHORITY explícito: {possible_xauth}")
            else:
                print(f"ℹ️ Usando DISPLAY existente: {env['DISPLAY']}")
        
            if env.get("DISPLAY"):
                try:
                    subprocess.run(["xhost", "+local:"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                except Exception as e:
                    print(f"⚠️ No se pudo ejecutar xhost: {e}")

        args = [
            python_executable,
            script_path,
            "--folder", folder_path,
            "--date", config.general.fecha, 
            "--ruc_sunat", config.sunat.ruc, 
            "--user_sunat", config.sunat.usuario, 
            "--password_sunat", config.sunat.claveSol, 
            "--correo_sap", config.sap.usuario, 
            "--password_sap", config.sap.password, 
            "--code_sociedad", config.general.sociedad
        ]

        if config.general.hora:
            args.extend(["--time", config.general.hora])

        if config.general.dias:
            args.extend(["--days", config.general.dias])
        
        socket_url = os.environ.get("SOCKET_URL")
        
        if not socket_url:
             socket_url = "http://127.0.0.1:8001"
             print(f"ℹ️ Configuración automática: Usando {socket_url} (Localhost)")

        print(f" Socket URL seleccionada para el bot: {socket_url}")
        args.extend(["--socket_url", socket_url])
        
        print(f"🚀 Ejecutando bot: {' '.join(args)}")
        
        # Force UTF-8 for the subprocess to avoid UnicodeEncodeError on Windows
        env["PYTHONIOENCODING"] = "utf-8"

        process = subprocess.Popen(
            args,
            cwd=service_dir,
            env=env,
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            encoding='utf-8'
        )
        
        loop = asyncio.get_running_loop()

        # Stream output function with debug prints
        def stream_output(proc, event_loop, exec_id):
            import re
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            
            try:
                print("🔵 Iniciando captura de logs del bot...")
                for line in proc.stdout:
                    if line:
                        # Detect if line has green color (validation/success)
                        is_green = '\033[92m' in line or '\033[32m' in line
                        
                        # Clean ANSI codes
                        clean_line = ansi_escape.sub('', line).strip()
                        
                        if clean_line:
                            # Filter out technical/debug logs
                            forbidden_markers = [
                                "Emitiendo evento", 
                                "{'message':", 
                                "{'date':", 
                                "Debug", "DEBUG", "debug",
                                "Socket Manager",
                                "Error de conexión",
                                "No se puede emitir evento",
                                "🌐 [CONSOLE]",
                                "HTTPConnectionPool",
                                "NewConnectionError",
                                "Max retries exceeded"
                            ]

                            if any(bad in clean_line for bad in forbidden_markers):
                                continue

                            # Whitelist: Only allow logs with specific icons as requested
                            allowed_markers = ["✅", "⬇️", "⚠️", "⚠", "❌", "📂", "🔍", "📄", "🚀", "🤖"]
                            if not any(ok in clean_line for ok in allowed_markers):
                               continue

                            # Add checkmark if it was green (for frontend styling)
                            if is_green and "✅" not in clean_line:
                                clean_line = f"✅ {clean_line}"

                            print(f"🤖 [BOT] {clean_line}")
                            
                            # Save to Database if execution_id is present
                            if exec_id:
                                try:
                                    db = SessionLocal()
                                    try:
                                        new_log = DSeguimiento(
                                            iMEjecucion=exec_id,
                                            tDescripcion=clean_line[:250], # Limit to 250 chars as per schema
                                            fRegistro=datetime.now()
                                        )
                                        db.add(new_log)
                                        db.commit()
                                    except Exception as db_err:
                                        print(f"⚠️ Error saving log to DB: {db_err}")
                                    finally:
                                        db.close()
                                except Exception as e:
                                    print(f"⚠️ Error creating DB session for logging: {e}")

                            asyncio.run_coroutine_threadsafe(
                                sio.emit('log:bot', {
                                    'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'message': clean_line
                                }),
                                event_loop
                            )
            except Exception as e:
                print(f"Error streaming logs: {e}")
            finally:
                print("🔴 Fin de captura de logs del bot")
                proc.stdout.close()

        t = threading.Thread(target=stream_output, args=(process, loop, config.execution_id))
        t.daemon = True
        t.start()
        
        return {"message": "Bot iniciado correctamente", "pid": process.pid}
        
    except Exception as e:
        print(f"Error ejecutando bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))
