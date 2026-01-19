from fastapi import APIRouter, HTTPException
import subprocess
import os

import sys

router = APIRouter()

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
