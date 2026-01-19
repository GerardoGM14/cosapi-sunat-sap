from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, utils, bot

app = FastAPI(title="AutoSUN - Cosapi OCR API", version="1.0.0")

# Configuración CORS (Permitir que Angular se conecte)
origins = [
    "http://localhost:4200",  # Angular default port
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(utils.router, prefix="/api/utils", tags=["Utils"])
app.include_router(bot.router, prefix="/api/bot", tags=["Bot"])

@app.get("/")
def read_root():
    return {"message": "Bienvenido a AutoSUN API - Cosapi"}
