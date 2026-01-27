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
    email: str
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
async def run_bot(config: BotConfig):
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
        
        # Como el usuario indica que "el .venv tambien tiene que ser del app.py", 
        # asumimos que debemos usar el entorno virtual del backend porque sunat-sap-service NO tiene .venv propio visible en LS.
        # Pero nos aseguramos de usar el python.exe del entorno virtual explícitamente.
        
        # Si estamos corriendo en un venv, sys.prefix apunta a él.
        python_executable = sys.executable
        
        # Si quisiéramos forzar un venv específico en sunat-sap-service (si el usuario lo crea luego):
        possible_service_venv = os.path.join(service_dir, ".venv", "Scripts", "python.exe")
        if os.path.exists(possible_service_venv):
            python_executable = possible_service_venv

        env = os.environ.copy()
        env["CONFIG_METHOD"] = "console" # Force console method to use CLI args
        env["PYTHONPATH"] = service_dir # Set pythonpath to service root

        # Configuración para mostrar navegador en Linux (si no es headless)
        if sys.platform == "linux":
            # Si no hay DISPLAY o está vacío, intentamos usar :0
            if not env.get("DISPLAY"):
                # IMPORTANTE: Para que funcione en una sesión de usuario real en Linux,
                # necesitamos apuntar al display correcto. Usualmente es :0 o :1.
                
                print("⚠️ Variable DISPLAY no encontrada o vacía. Asignando DISPLAY=:0")
                env["DISPLAY"] = ":0"
                
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
        if sys.platform == "linux" and env.get("DISPLAY"):
            try:
                # Ejecutar xhost +local: para permitir conexiones locales
                # Usamos el mismo entorno con XAUTHORITY configurado
                subprocess.run(["xhost", "+local:"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                print("ℹ️ Intenté ejecutar 'xhost +local:' para dar permisos gráficos.")
            except Exception as e:
                print(f"⚠️ No se pudo ejecutar xhost: {e}")


        # Normalizar ruta a formato Windows (backslashes) para evitar problemas y cumplir con preferencia de usuario
        folder_path = os.path.normpath(config.general.folder)

        # Construct command with CLI arguments as requested
        # NOTA: subprocess.Popen con lista maneja el quoting automáticamente para el sistema operativo.
        # No debemos añadir comillas extra a los valores aquí o llegarán duplicadas (ej: '"valor"').
        cmd_args = [
            python_executable,
            script_path,
            "--folder", folder_path,
            "--code_sociedad", config.general.sociedad,
            "--date", config.general.fecha,
            "--ruc_sunat", config.sunat.ruc,
            "--user_sunat", config.sunat.usuario,
            "--password_sunat", config.sunat.claveSol,
            "--correo_sap", config.sap.email,
            "--password_sap", config.sap.password
        ]

        # Convert to string for display (masking nothing as requested "deberia de verse la clave")
        # Forzamos comillas en el LOG para que el usuario pueda copiar y pegar el comando en terminal Windows
        def quote_for_log(arg):
            # Si empieza con -- o es el ejecutable/script, lo dejamos igual (a menos que tenga espacios)
            if arg.startswith("--") or arg == python_executable or arg == script_path:
                if " " in arg: return f'"{arg}"'
                return arg
            # Para los valores, forzamos comillas para asegurar formato "C:\Ruta"
            return f'"{arg}"'

        full_command_str = " ".join([quote_for_log(arg) for arg in cmd_args])

        # Archivo de logs
        log_file_path = os.path.join(service_dir, "bot_execution.log")
        
        print("\n" + "="*60)
        print("🚀 COMANDO DE EJECUCIÓN (VISIBLE EN TERMINAL):")
        print("="*60)
        print(f"📂 CWD (Directorio de trabajo): {service_dir}")
        print(f"🐍 Python Executable          : {python_executable}")
        print(f"📝 Log File                   : {log_file_path}")
        print(full_command_str)
        print("="*60)
        
        # Abrir archivo de log en modo append
        log_file = open(log_file_path, "w", encoding="utf-8")
        
        # Escribir cabecera en el log
        log_file.write(f"--- START EXECUTION: {config.general.fecha} ---\n")
        log_file.write(f"Command: {full_command_str}\n")
        
        # Debug: Log environment variables relevant to display
        if sys.platform == "linux":
            log_file.write(f"DEBUG ENV: DISPLAY={env.get('DISPLAY')}\n")
            log_file.write(f"DEBUG ENV: XAUTHORITY={env.get('XAUTHORITY')}\n")
            log_file.write(f"DEBUG ENV: USER={env.get('USER')}\n")
            
        log_file.write("-" * 50 + "\n")
        log_file.flush()

        # Ejecutar en segundo plano redirigiendo salida al archivo
        process = subprocess.Popen(
            cmd_args,
            cwd=service_dir, # IMPORTANTE: Ejecutar desde la carpeta del servicio
            env=env,
            text=True,
            stdout=log_file,
            stderr=subprocess.STDOUT # Redirigir stderr a stdout (mismo archivo)
        )
        
        # No cerramos log_file aquí inmediatamente porque el proceso lo usa,
        # pero como es Popen, el file handle se pasa al proceso hijo.
        # Sin embargo, en Python, si cerramos el handle en el padre, el hijo sigue teniendo acceso?
        # Sí, pero para estar seguros y evitar ResourceWarning, podemos dejarlo que el GC lo maneje 
        # o simplemente confiar en que subprocess duplica el descriptor.
        # Lo correcto es no cerrarlo explícitamente si queremos seguir escribiendo desde el padre, 
        # pero aquí ya no escribimos más.
        # De hecho, subprocess.Popen toma el file descriptor.
        
        return {
            "status": "success", 
            "message": "El proceso ha iniciado correctamente. Revise bot_execution.log para detalles.", 
            "pid": process.pid,
            "log_file": log_file_path
        }

    except Exception as e:
        print(f"Error running bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))
