from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess
import sys
import os
import asyncio

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
        # Validar carpeta
        if not config.general.folder:
            raise HTTPException(status_code=400, detail="La carpeta de salida es requerida")

        # Construir el comando
        # python sunat-sap-service/app.py --folder "..." ...
        
        # Asumimos que sunat-sap-service está en el directorio raíz del proyecto
        # y que el backend se ejecuta desde backend/ o root.
        # Ajustamos la ruta base para obtener rutas absolutas
        current_dir = os.getcwd()
        
        # Intentar localizar la carpeta del servicio subiendo un nivel si estamos en backend
        possible_service_dir = os.path.abspath(os.path.join(current_dir, "..", "sunat-sap-service"))
        
        if not os.path.exists(possible_service_dir):
             # Si no existe, probar si estamos en la raíz y la carpeta está ahí
             possible_service_dir = os.path.abspath(os.path.join(current_dir, "sunat-sap-service"))
        
        service_dir = possible_service_dir
        script_path = os.path.join(service_dir, "app.py")
        
        if not os.path.exists(script_path):
             # Fallback hardcoded por si acaso la estructura es muy distinta
             script_path = r"c:\Users\Soporte\Documents\Proyectos\ocr-cosapi-full\sunat-sap-service\app.py"
             service_dir = os.path.dirname(script_path)

        # Determinar el intérprete de Python a usar
        # Prioridad 1: .venv dentro de sunat-sap-service (si existiera)
        # Prioridad 2: .venv del backend (actualmente en uso)
        # Prioridad 3: sys.executable actual
        
        python_executable = sys.executable
        
        possible_service_venv = os.path.join(service_dir, ".venv", "Scripts", "python.exe")
        if os.path.exists(possible_service_venv):
            python_executable = possible_service_venv

        env = os.environ.copy()
        env["CONFIG_METHOD"] = "console" # Force console method to use CLI args
        env["PYTHONPATH"] = service_dir # Set pythonpath to service root

        # Configuración para mostrar navegador en Linux (si no es headless)
        if sys.platform == "linux":
            # Si no hay DISPLAY o está vacío, intentamos configurarlo
            if not env.get("DISPLAY"):
                # Primero, intentamos leer si existe un archivo .env en sunat-sap-service que tenga DISPLAY
                # Esto permite configuración manual por parte del usuario
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
                    # Fallback por defecto.
                    print("⚠️ Variable DISPLAY no encontrada o vacía. Asignando DISPLAY=:1 (predeterminado para este servidor)")
                    env["DISPLAY"] = ":1"
                
                # Intentar encontrar el archivo .Xauthority del usuario actual
                home_dir = os.path.expanduser("~")
                xauth_path = os.path.join(home_dir, ".Xauthority")
                
                if os.path.exists(xauth_path):
                    env["XAUTHORITY"] = xauth_path
                    print(f"ℹ️ Usando XAUTHORITY: {xauth_path}")
                else:
                    # Fallback
                    possible_xauth = "/home/sertech/.Xauthority"
                    if os.path.exists(possible_xauth):
                         env["XAUTHORITY"] = possible_xauth
                         print(f"ℹ️ Usando XAUTHORITY explícito: {possible_xauth}")
            else:
                print(f"ℹ️ Usando DISPLAY existente: {env['DISPLAY']}")
        
            # Intentar dar permisos con xhost (solo si tenemos DISPLAY)
            if env.get("DISPLAY"):
                try:
                    subprocess.run(["xhost", "+local:"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                except Exception as e:
                    print(f"⚠️ No se pudo ejecutar xhost: {e}")


        # Normalizar ruta a formato Windows (backslashes)
        folder_path = os.path.normpath(config.general.folder)

        # Construir argumentos para CLI
        args = [
            python_executable,
            script_path,
            "--folder", folder_path,
            "--fecha", config.general.fecha,
            "--ruc", config.sunat.ruc,
            "--usuario-sunat", config.sunat.usuario,
            "--clave-sunat", config.sunat.claveSol,
            "--usuario-sap", config.sap.usuario,
            "--password-sap", config.sap.password,
            "--sociedad", config.general.sociedad
        ]
        
        print(f"🚀 Ejecutando bot: {' '.join(args)}")
        
        process = subprocess.Popen(
            args,
            cwd=service_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return {"message": "Bot iniciado correctamente", "pid": process.pid}
        
    except Exception as e:
        print(f"Error ejecutando bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))
