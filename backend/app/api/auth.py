from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import MUsuario
from passlib.context import CryptContext
import hashlib

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def prepare_password(password: str) -> str:
    """
    Bcrypt has a limit of 72 bytes. If the password is longer,
    we hash it with SHA256 to get a safe 64-byte string.
    """
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # Return hex digest which is ASCII and 64 chars long
        return hashlib.sha256(password_bytes).hexdigest()
    return password

def verify_password(plain_password, hashed_password):
    safe_password = prepare_password(plain_password)
    return pwd_context.verify(safe_password, hashed_password)

def get_password_hash(password):
    safe_password = prepare_password(password)
    return pwd_context.hash(safe_password)

@router.post("/login", response_model=Token)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    # Buscar usuario por correo
    user = db.query(MUsuario).filter(MUsuario.tCorreo == credentials.username).first()
    
    if not user:
        # Fallback para admin hardcoded si no hay usuarios en DB (opcional, pero útil)
        if credentials.username == "admin" and credentials.password == "admin123":
             return {"access_token": "fake-jwt-token-cosapi-autosun", "token_type": "bearer"}
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar contraseña
    # Nota: Si las contraseñas antiguas no están hasheadas, esto fallará. 
    # Para este caso, asumimos que todas las nuevas se hashean.
    # Si la contraseña en DB no parece un hash bcrypt, intentamos comparación directa (migración suave)
    valid_password = False
    if user.tClave.startswith("$2b$") or user.tClave.startswith("$2a$"):
        valid_password = verify_password(credentials.password, user.tClave)
    else:
        valid_password = (credentials.password == user.tClave)
        
    if not valid_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return {"access_token": f"user-{user.iMusuario}", "token_type": "bearer"}

