# Script para iniciar el servidor backend correctamente permitiendo conexiones externas
Write-Host "Iniciando AutoSUN Backend en 0.0.0.0:8001..." -ForegroundColor Green

# Asegurar que estamos en el directorio correcto
Set-Location -Path "c:\Users\Soporte\Documents\Proyectos\ocr-cosapi-full\backend"

# Activar entorno virtual y ejecutar uvicorn
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
