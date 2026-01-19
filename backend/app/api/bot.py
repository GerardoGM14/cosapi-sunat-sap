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

        print("\n" + "="*60)
        print("🚀 COMANDO DE EJECUCIÓN (VISIBLE EN TERMINAL):")
        print("="*60)
        print(f"📂 CWD (Directorio de trabajo): {service_dir}")
        print(f"🐍 Python Executable          : {python_executable}")
        print(full_command_str)
        print("="*60)
        print("⚠️  NOTA: Los logs del proceso aparecerán a continuación en esta misma terminal.")
        print("="*60 + "\n")

        # Ejecutar en segundo plano
        # Se modificó para heredar la consola actual y mostrar logs directamente aquí
        process = subprocess.Popen(
            cmd_args,
            cwd=service_dir, # IMPORTANTE: Ejecutar desde la carpeta del servicio
            env=env,
            text=True
            # Se eliminó creationflags=subprocess.CREATE_NEW_CONSOLE para no abrir ventana separada
            # Se eliminó stdout/stderr=PIPE para que herede la salida de este proceso (terminal visible)
        )
        
        # No esperamos el resultado completo aquí para no bloquear, 
        # pero podríamos leer las primeras líneas o simplemente confirmar inicio.
        # Dado que es un proceso largo, retornamos éxito inmediato.
        
        return {
            "status": "success", 
            "message": "El proceso ha iniciado correctamente.", 
            "pid": process.pid
        }

    except Exception as e:
        print(f"Error running bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))
