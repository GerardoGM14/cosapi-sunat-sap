from fastapi import APIRouter, HTTPException, Body, Depends
import subprocess
import os
import sys
import json
from pydantic import BaseModel
from dotenv import dotenv_values
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import MSap
from datetime import datetime

router = APIRouter()

@router.get("/check-service")
async def check_service():
    try:
        current_dir = os.getcwd()
        possible_service_dir = os.path.abspath(os.path.join(current_dir, "..", "sunat-sap-service"))
        if not os.path.exists(possible_service_dir):
             possible_service_dir = os.path.abspath(os.path.join(current_dir, "sunat-sap-service"))
        
        script_path = os.path.join(possible_service_dir, "app.py")
        env_path = os.path.join(possible_service_dir, ".env")
        
        headless_status = "Unknown"
        if os.path.exists(env_path):
            config = dotenv_values(env_path)
            headless_status = config.get("HEADLESS", "true (default)")
        else:
            headless_status = "true (default - .env missing)"
        
        if os.path.exists(script_path):
            return {
                "status": "ok", 
                "message": "Service scripts found.", 
                "headless_mode": headless_status,
                "service_path": possible_service_dir
            }
        else:
            return {"status": "error", "message": "Service scripts not found (app.py missing)."}
    except Exception as e:
         return {"status": "error", "message": str(e)}

@router.post("/list-folders")
async def list_folders(payload: dict = Body(...)):
    try:
        current_path = payload.get("path")

        if not current_path or current_path == "":
            current_path = os.getcwd()
            
        if not os.path.exists(current_path):
            current_path = os.getcwd()

        items = []
        try:
            with os.scandir(current_path) as entries:
                for entry in entries:
                    if entry.is_dir():
                        items.append(entry.name)
        except PermissionError:
            pass

        items.sort()

        parent_path = os.path.dirname(current_path)
        if parent_path == current_path:
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

# --- SAP Configuration Endpoints ---

class SapConfig(BaseModel):
    usuario: str
    password: str

def get_service_params_dir():
    current_dir = os.getcwd()
    possible_service_dir = os.path.abspath(os.path.join(current_dir, "..", "sunat-sap-service"))
    if not os.path.exists(possible_service_dir):
         possible_service_dir = os.path.abspath(os.path.join(current_dir, "sunat-sap-service"))
    
    params_dir = os.path.join(possible_service_dir, "src", "parameters")
    os.makedirs(params_dir, exist_ok=True)
    return params_dir

@router.get("/config/sap")
async def get_sap_config():
    try:
        params_dir = get_service_params_dir()
        file_path = os.path.join(params_dir, "sap_config.json")
        
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {"usuario": "", "password": ""}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/config/sap")
async def save_sap_config(config: SapConfig, db: Session = Depends(get_db)):
    try:
        params_dir = get_service_params_dir()
        file_path = os.path.join(params_dir, "sap_config.json")
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(config.dict(), f, indent=4)

        db_sap = db.query(MSap).filter(MSap.tUsuario == config.usuario).first()
        
        if db_sap:
            db_sap.tClave = config.password
            db_sap.fModificacion = datetime.utcnow()
            db_sap.lActivo = True
        else:
            new_sap = MSap(
                tUsuario=config.usuario,
                tClave=config.password,
                lActivo=True,
                fRegistro=datetime.utcnow()
            )
            db.add(new_sap)
            
        db.commit()
            
        return {"status": "success", "message": "Configuración SAP guardada en archivo y base de datos"}
    except Exception as e:
        print(f"Error saving SAP config: {e}")
        raise HTTPException(status_code=500, detail=str(e))
