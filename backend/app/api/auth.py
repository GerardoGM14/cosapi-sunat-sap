from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/login", response_model=Token)
async def login(credentials: LoginRequest):
    # TODO: Conectar con Base de Datos real
    # Mock login para prototipo
    if credentials.username == "admin" and credentials.password == "admin123":
        return {"access_token": "fake-jwt-token-cosapi-autosun", "token_type": "bearer"}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales incorrectas",
        headers={"WWW-Authenticate": "Bearer"},
    )
