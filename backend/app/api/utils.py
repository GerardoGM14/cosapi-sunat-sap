from fastapi import APIRouter, HTTPException, Body
import subprocess
import os
import sys

router = APIRouter()

@router.get("/check-service")
async def check_service():
    """Verifica si el servicio de Sunat/Sap (scripts) es accesible."""
    try:
        # Lógica similar a bot.py para encontrar la carpeta
        current_dir = os.getcwd()
        possible_service_dir = os.path.abspath(os.path.join(current_dir, "..", "sunat-sap-service"))
        if not os.path.exists(possible_service_dir):
             possible_service_dir = os.path.abspath(os.path.join(current_dir, "sunat-sap-service"))
        
        script_path = os.path.join(possible_service_dir, "app.py")
        
        if os.path.exists(script_path):
            return {"status": "ok", "message": "Service scripts found."}
        else:
            return {"status": "error", "message": "Service scripts not found (app.py missing)."}
    except Exception as e:
         return {"status": "error", "message": str(e)}

@router.post("/list-folders")
async def list_folders(payload: dict = Body(...)):
    try:
        current_path = payload.get("path")
        
        # Si no hay path, usar el directorio actual o C:\
        if not current_path or current_path == "":
            current_path = os.getcwd()
            
        if not os.path.exists(current_path):
            current_path = os.getcwd()

        # Listar directorios
        items = []
        try:
            with os.scandir(current_path) as entries:
                for entry in entries:
                    if entry.is_dir():
                        items.append(entry.name)
        except PermissionError:
            pass # Ignorar carpetas sin permiso

        items.sort()
        
        # Obtener padre
        parent_path = os.path.dirname(current_path)
        if parent_path == current_path: # Root
            parent_path = None

        return {
            "current_path": current_path,
            "parent_path": parent_path,
            "folders": items
        }

    except Exception as e:
        print(f"Error listing folders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/select-folder")
async def select_folder():
    try:
        # Usar Tkinter en un subproceso para abrir el diálogo nativo moderno
        cmd = [
            sys.executable, 
            "-c", 
            "import tkinter as tk; from tkinter import filedialog; root = tk.Tk(); root.withdraw(); root.attributes('-topmost', True); print(filedialog.askdirectory())"
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        
        if stderr:
            print(f"Dialog Stderr: {stderr}")
            
        folder_path = stdout.strip()
        
        if not folder_path:
            return {"folder": None}
            
        return {"folder": folder_path}
        
    except Exception as e:
        print(f"Error selecting folder: {e}")
        raise HTTPException(status_code=500, detail=str(e))
