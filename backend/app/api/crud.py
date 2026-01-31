from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import SessionLocal
from app.models import MSociedad
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Schemas
class SociedadBase(BaseModel):
    tRuc: str
    tRazonSocial: str
    tUsuario: str | None = None
    tClave: str | None = None
    lActivo: bool = True

class SociedadCreate(SociedadBase):
    pass

class SociedadUpdate(BaseModel):
    tRazonSocial: str | None = None
    tUsuario: str | None = None
    tClave: str | None = None
    lActivo: bool | None = None

class SociedadResponse(SociedadBase):
    fRegistro: datetime | None = None

    class Config:
        orm_mode = True

# Endpoints

@router.get("/sociedades", response_model=List[SociedadResponse])
def read_sociedades(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sociedades = db.query(MSociedad).offset(skip).limit(limit).all()
    return sociedades

@router.post("/sociedades", response_model=SociedadResponse)
def create_sociedad(sociedad: SociedadCreate, db: Session = Depends(get_db)):
    db_sociedad = db.query(MSociedad).filter(MSociedad.tRuc == sociedad.tRuc).first()
    if db_sociedad:
        raise HTTPException(status_code=400, detail="Sociedad con este RUC ya existe")
    
    new_sociedad = MSociedad(**sociedad.dict())
    db.add(new_sociedad)
    db.commit()
    db.refresh(new_sociedad)
    return new_sociedad

@router.put("/sociedades/{ruc}", response_model=SociedadResponse)
def update_sociedad(ruc: str, sociedad: SociedadUpdate, db: Session = Depends(get_db)):
    db_sociedad = db.query(MSociedad).filter(MSociedad.tRuc == ruc).first()
    if not db_sociedad:
        raise HTTPException(status_code=404, detail="Sociedad no encontrada")
    
    update_data = sociedad.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_sociedad, key, value)
    
    db.commit()
    db.refresh(db_sociedad)
    return db_sociedad

@router.delete("/sociedades/{ruc}")
def delete_sociedad(ruc: str, db: Session = Depends(get_db)):
    db_sociedad = db.query(MSociedad).filter(MSociedad.tRuc == ruc).first()
    if not db_sociedad:
        raise HTTPException(status_code=404, detail="Sociedad no encontrada")
    
    db.delete(db_sociedad)
    db.commit()
    return {"message": "Sociedad eliminada exitosamente"}
