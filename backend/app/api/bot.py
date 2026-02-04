from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess
import sys
import os
import asyncio
import threading
from datetime import datetime
from app.socket_manager import sio

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
    folder: str

class BotConfig(BaseModel):
    sunat: SunatConfig
    sap: SapConfig
    general: GeneralConfig

@router.post("/run")
async def run_bot_endpoint(config: BotConfig):
    return await run_bot_logic(config)

async def run_bot_logic(config: BotConfig):
    try:
        if not config.general.folder:
            raise HTTPException(status_code=400, detail="La carpeta de salida es requerida")
        current_dir = os.getcwd()
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

        folder_path = os.path.normpath(config.general.folder)

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
        
        print(f"🚀 Ejecutando bot: {' '.join(args)}")
        
        # Capture output and stream via socket
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

        def stream_output(proc, event_loop):
            try:
                print("🔵 Iniciando captura de logs del bot...")
                for line in proc.stdout:
                    if line:
                        clean_line = line.strip()
                        print(f"🤖 [BOT STDOUT] {clean_line}")
                        if clean_line:
                            asyncio.run_coroutine_threadsafe(
                                sio.emit('log:bot', {
                                    'date': datetime.now().strftime("%H:%M:%S"),
                                    'message': clean_line
                                }),
                                event_loop
                            )
            except Exception as e:
                print(f"Error streaming logs: {e}")
            finally:
                print("🔴 Fin de captura de logs del bot")
                proc.stdout.close()

        t = threading.Thread(target=stream_output, args=(process, loop))
        t.daemon = True
        t.start()
        
        return {"message": "Bot iniciado correctamente", "pid": process.pid}
        
    except Exception as e:
        print(f"Error ejecutando bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))
