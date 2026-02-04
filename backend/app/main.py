import socketio
from app.socket_manager import sio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, utils, bot, crud
from app.database import engine, Base, SessionLocal
from app import models 
from app.models import MRol

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

def seed_roles():
    db = SessionLocal()
    try:
        if db.query(MRol).count() == 0:
            roles = [
                MRol(iMRol=1, tRol="Administrador", lActivo=True),
                MRol(iMRol=2, tRol="Usuario", lActivo=True)
            ]
            db.add_all(roles)
            db.commit()
            print("Roles iniciales creados.")
    except Exception as e:
        print(f"Error creando roles: {e}")
    finally:
        db.close()

seed_roles()

app = FastAPI(title="AutoSUN - Cosapi OCR API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(utils.router, prefix="/api/utils", tags=["Utils"])
app.include_router(bot.router, prefix="/api/bot", tags=["Bot"])
app.include_router(crud.router, prefix="/api/crud", tags=["CRUD"])

@app.get("/")
def read_root():
    return {"message": "Bienvenido a AutoSUN API - Cosapi"}

@app.on_event("startup")
async def startup_event():
    from app.scheduler import start_scheduler
    start_scheduler()

app = socketio.ASGIApp(sio, other_asgi_app=app)
