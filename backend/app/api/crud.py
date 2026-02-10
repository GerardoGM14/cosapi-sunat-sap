from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.database import SessionLocal, get_db
from app.models import MSociedad, MUsuario, MSap, MSapSociedad, MProgramacion, MProgramacionSociedad, DEjecucion, MListaBlanca, MListaBlancaSociedad, DSeguimiento
from app.api.auth import get_password_hash
from app.services.execution import execute_programacion_logic, execute_sociedad_logic
from pydantic import BaseModel
from datetime import datetime
import pandas as pd
import io

router = APIRouter()

class SociedadBase(BaseModel):
    tRuc: str
    tCodigoSap: str | None = None
    tRazonSocial: str
    tUsuario: str | None = None
    tClave: str | None = None
    lActivo: bool = True

class SociedadCreate(SociedadBase):
    pass

class SociedadUpdate(BaseModel):
    tCodigoSap: str | None = None
    tRazonSocial: str | None = None
    tUsuario: str | None = None
    tClave: str | None = None
    lActivo: bool | None = None

class SociedadResponse(SociedadBase):
    fRegistro: datetime | None = None

    class Config:
        from_attributes = True

class UsuarioBase(BaseModel):
    tNombre: str
    tApellidos: str
    tCorreo: str
    tClave: str
    iMRol: int | None = None
    lNotificacion: bool = True
    lActivo: bool = True

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioUpdate(BaseModel):
    tNombre: str | None = None
    tApellidos: str | None = None
    tCorreo: str | None = None
    tClave: str | None = None
    iMRol: int | None = None
    lNotificacion: bool | None = None
    lActivo: bool | None = None

class UsuarioResponse(UsuarioBase):
    iMusuario: int
    fRegistro: datetime | None = None

    class Config:
        from_attributes = True

class SapBase(BaseModel):
    tUsuario: str
    tClave: str
    lActivo: bool = True

class SapCreate(SapBase):
    pass

class SapResponse(SapBase):
    iMSAP: int
    fRegistro: datetime | None = None

    class Config:
        from_attributes = True

@router.get("/sap-accounts", response_model=List[SapResponse])
def get_all_sap_accounts(db: Session = Depends(get_db)):
    return db.query(MSap).filter(MSap.lActivo == True).all()

@router.get("/sociedades/{ruc}/sap-accounts", response_model=List[SapResponse])
def get_sociedad_sap_accounts(ruc: str, db: Session = Depends(get_db)):
    sociedad = db.query(MSociedad).filter(MSociedad.tRuc == ruc).first()
    if not sociedad:
        sociedad = db.query(MSociedad).filter(MSociedad.tCodigoSap == ruc).first()
        
    if not sociedad:
        raise HTTPException(status_code=404, detail="Sociedad no encontrada")
    cuentas = db.query(MSap).join(MSapSociedad).filter(MSapSociedad.tRuc == sociedad.tRuc, MSapSociedad.lActivo == True).all()
    
    return cuentas

@router.post("/sociedades/{ruc}/sap-accounts/{sap_id}")
def associate_sap_to_sociedad(ruc: str, sap_id: int, db: Session = Depends(get_db)):
    sociedad = db.query(MSociedad).filter(MSociedad.tRuc == ruc).first()
    if not sociedad:
        raise HTTPException(status_code=404, detail="Sociedad no encontrada")
        
    sap = db.query(MSap).filter(MSap.iMSAP == sap_id).first()
    if not sap:
        raise HTTPException(status_code=404, detail="Cuenta SAP no encontrada")
    exists = db.query(MSapSociedad).filter(
        MSapSociedad.tRuc == ruc,
        MSapSociedad.iMSAP == sap_id
    ).first()
    
    if exists:
        return {"message": "La relación ya existe"}
        
    new_relation = MSapSociedad(tRuc=ruc, iMSAP=sap_id)
    db.add(new_relation)
    db.commit()

    save_parameters_to_file(db)
    
    return {"message": "Cuenta SAP asociada exitosamente"}

@router.get("/usuarios", response_model=List[UsuarioResponse])
def read_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    usuarios = db.query(MUsuario).offset(skip).limit(limit).all()
    return usuarios

@router.post("/usuarios", response_model=UsuarioResponse)
def create_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = db.query(MUsuario).filter(MUsuario.tCorreo == usuario.tCorreo).first()
    if db_usuario:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    
    hashed_password = get_password_hash(usuario.tClave)
    
    new_usuario = MUsuario(
        tNombre=usuario.tNombre,
        tApellidos=usuario.tApellidos,
        tCorreo=usuario.tCorreo,
        tClave=hashed_password,
        iMRol=usuario.iMRol,
        lNotificacion=usuario.lNotificacion,
        lActivo=usuario.lActivo,
        fRegistro=datetime.now()
    )
    db.add(new_usuario)
    db.commit()
    db.refresh(new_usuario)
    return new_usuario

@router.delete("/usuarios/{user_id}")
def delete_usuario(user_id: int, db: Session = Depends(get_db)):
    db_usuario = db.query(MUsuario).filter(MUsuario.iMusuario == user_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    db.delete(db_usuario)
    db.commit()
    return {"message": "Usuario eliminado exitosamente"}

@router.put("/usuarios/{user_id}", response_model=UsuarioResponse)
def update_usuario(user_id: int, usuario: UsuarioUpdate, db: Session = Depends(get_db)):
    db_usuario = db.query(MUsuario).filter(MUsuario.iMusuario == user_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if usuario.tNombre is not None:
        db_usuario.tNombre = usuario.tNombre
    if usuario.tApellidos is not None:
        db_usuario.tApellidos = usuario.tApellidos
    if usuario.tCorreo is not None:
        if usuario.tCorreo != db_usuario.tCorreo:
            existing_user = db.query(MUsuario).filter(MUsuario.tCorreo == usuario.tCorreo).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="El correo ya está en uso")
        db_usuario.tCorreo = usuario.tCorreo
    if usuario.tClave is not None and usuario.tClave != "":
         db_usuario.tClave = get_password_hash(usuario.tClave)
    if usuario.iMRol is not None:
        db_usuario.iMRol = usuario.iMRol
    if usuario.lNotificacion is not None:
        db_usuario.lNotificacion = usuario.lNotificacion
    if usuario.lActivo is not None:
        db_usuario.lActivo = usuario.lActivo
        
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@router.get("/sociedades", response_model=List[SociedadResponse])
def read_sociedades(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sociedades = db.query(MSociedad).offset(skip).limit(limit).all()
    return sociedades

import os
import json

def save_parameters_to_file(db: Session):
    try:
        results = db.query(MSociedad, MSap).\
            outerjoin(MSapSociedad, MSociedad.tRuc == MSapSociedad.tRuc).\
            outerjoin(MSap, MSapSociedad.iMSAP == MSap.iMSAP).\
            all()
        data = []
        for sociedad, sap in results:
            item = {
                "code_sociedad": sociedad.tCodigoSap,
                "ruc_sunat": sociedad.tRuc,
                "razon_social": sociedad.tRazonSocial,
                "user_sunat": sociedad.tUsuario,
                "password_sunat": sociedad.tClave,
                "active": sociedad.lActivo,
                "sap_user": sap.tUsuario if sap else None,
                "sap_password": sap.tClave if sap else None
            }
            data.append(item)

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        service_dir = os.path.join(base_dir, "sunat-sap-service")
        
        if not os.path.exists(service_dir):
            return
            
        params_file = os.path.join(service_dir, "parameters.json")
        
        with open(params_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        print(f"Parámetros actualizados guardados en {params_file}")
        
    except Exception as e:
        print(f"Error guardando parámetros: {e}")

@router.post("/sociedades", response_model=SociedadResponse)
def create_sociedad(sociedad: SociedadCreate, db: Session = Depends(get_db)):
    if not sociedad.tRuc or not sociedad.tRuc.strip():
        raise HTTPException(status_code=400, detail="El RUC no puede estar vacío")
    
    db_sociedad = db.query(MSociedad).filter(MSociedad.tRuc == sociedad.tRuc).first()
    if db_sociedad:
        raise HTTPException(status_code=400, detail="Sociedad con este RUC ya existe")
    
    new_sociedad = MSociedad(**sociedad.dict())
    db.add(new_sociedad)
    db.commit()
    db.refresh(new_sociedad)
    save_parameters_to_file(db)
    
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
    save_parameters_to_file(db)
    
    return db_sociedad

@router.delete("/sociedades")
def delete_bad_sociedades(db: Session = Depends(get_db)):
    deleted = db.query(MSociedad).filter((MSociedad.tRuc == "") | (MSociedad.tRuc == None)).delete()
    db.commit()
    if deleted > 0:
        return {"message": f"Se eliminaron {deleted} registros corruptos (RUC vacío)"}
    return {"message": "No se encontraron registros con RUC vacío"}

@router.delete("/sociedades/{ruc}")
def delete_sociedad(ruc: str, db: Session = Depends(get_db)):
    db_sociedad = db.query(MSociedad).filter(MSociedad.tRuc == ruc).first()
    if not db_sociedad:
        raise HTTPException(status_code=404, detail="Sociedad no encontrada")
    
    db.delete(db_sociedad)
    db.commit()
    return {"message": "Sociedad eliminada exitosamente"}

# Programacion Endpoints

class ProgramacionCreate(BaseModel):
    tNombre: str
    tHora: str
    tDias: List[str]
    sociedades: List[str]
    lActivo: bool = True

class ProgramacionResponse(BaseModel):
    iMProgramacion: int
    tNombre: str
    tHora: str
    tDias: List[str]
    iSociedadesCount: int
    lActivo: bool
    
    class Config:
        from_attributes = True

def map_programacion_response(p: MProgramacion):
    return ProgramacionResponse(
        iMProgramacion=p.iMProgramacion,
        tNombre=p.tNombre,
        tHora=p.tHora,
        tDias=p.tDias.split(',') if p.tDias else [],
        iSociedadesCount=p.iSociedadesCount,
        lActivo=p.lActivo
    )

@router.get("/programacion", response_model=List[ProgramacionResponse])
def get_programaciones(db: Session = Depends(get_db)):
    programaciones = db.query(MProgramacion).all()
    return [map_programacion_response(p) for p in programaciones]

@router.post("/programacion", response_model=ProgramacionResponse)
def create_programacion(programacion: ProgramacionCreate, db: Session = Depends(get_db)):
    dias_str = ",".join(programacion.tDias)
    
    new_prog = MProgramacion(
        tNombre=programacion.tNombre,
        tHora=programacion.tHora,
        tDias=dias_str,
        iSociedadesCount=len(programacion.sociedades),
        lActivo=programacion.lActivo
    )
    db.add(new_prog)
    db.commit()
    db.refresh(new_prog)
    
    for ruc in programacion.sociedades:
        rel = MProgramacionSociedad(
            iMProgramacion=new_prog.iMProgramacion,
            tRuc=ruc
        )
        db.add(rel)
    db.commit()
    
    return map_programacion_response(new_prog)

@router.delete("/programacion/{id}")
def delete_programacion(id: int, db: Session = Depends(get_db)):
    prog = db.query(MProgramacion).filter(MProgramacion.iMProgramacion == id).first()
    if not prog:
        raise HTTPException(status_code=404, detail="Programación no encontrada")
    
    db.delete(prog)
    db.commit()
    return {"message": "Programación eliminada exitosamente"}

@router.put("/programacion/{id}/toggle")
def toggle_programacion(id: int, db: Session = Depends(get_db)):
    prog = db.query(MProgramacion).filter(MProgramacion.iMProgramacion == id).first()
    if not prog:
        raise HTTPException(status_code=404, detail="Programación no encontrada")
    
    prog.lActivo = not prog.lActivo
    db.commit()
    db.refresh(prog)
    
    return {"message": "Estado actualizado", "lActivo": prog.lActivo}

# Execution Dashboard Endpoints

class ExecutionHistoryItem(BaseModel):
    iMEjecucion: int
    fecha: str
    nombre: str
    tipo: str
    detalle: str
    estado: str

class ExecutionActiveItem(BaseModel):
    id: int
    nombre: str
    tipo: str
    detalle: str
    progreso: int
    logs: List[dict] = []
    
class ExecutionDashboardResponse(BaseModel):
    active: List[ExecutionActiveItem]
    history: List[ExecutionHistoryItem]

class LogItem(BaseModel):
    date: str
    message: str

@router.get("/ejecuciones/{execution_id}/logs", response_model=List[LogItem])
def get_execution_logs(execution_id: int, db: Session = Depends(get_db)):
    logs = db.query(DSeguimiento).filter(DSeguimiento.iMEjecucion == execution_id).order_by(DSeguimiento.fRegistro.asc()).all()
    
    result = []
    for log in logs:
        result.append(LogItem(
            date=log.fRegistro.strftime("%Y-%m-%d %H:%M:%S") if log.fRegistro else "",
            message=log.tDescripcion or ""
        ))
    return result

@router.get("/sociedades/{ruc}/ejecuciones", response_model=ExecutionDashboardResponse)
def get_sociedad_ejecuciones(ruc: str, db: Session = Depends(get_db)):
    programaciones = db.query(MProgramacion).join(MProgramacionSociedad).filter(
        MProgramacionSociedad.tRuc == ruc,
        MProgramacion.lActivo == True
    ).all()
    
    active_items = []
    for p in programaciones:
        active_items.append(ExecutionActiveItem(
            id=p.iMProgramacion,
            nombre=p.tNombre,
            tipo="Programación",
            detalle=f"Prog.: {p.tHora} - {p.tDias}",
            progreso=0,
            logs=[]
        ))
        
    ejecuciones = db.query(DEjecucion).filter(DEjecucion.tRuc == ruc).order_by(DEjecucion.fRegistro.desc()).limit(10).all()
    
    history_items = []
    for e in ejecuciones:
        history_items.append(ExecutionHistoryItem(
            iMEjecucion=e.iMEjecucion,
            fecha=e.fRegistro.strftime("%d/%m/%Y • %H:%M") if e.fRegistro else "",
            nombre=f"Ejecución #{e.iMEjecucion}",
            tipo="Manual" if e.tTipo == 'M' else "Automático",
            detalle=f"Usuario ID: {e.iUsuarioEjecucion}" if e.iUsuarioEjecucion else "Sistema",
            estado="Completado"
        ))
        
    return ExecutionDashboardResponse(active=active_items, history=history_items)

class ExecuteProgramacionRequest(BaseModel):
    date: Optional[str] = None

@router.post("/programacion/{id}/execute")
async def execute_programacion_manual(id: int, request: ExecuteProgramacionRequest = None, ruc: Optional[str] = None, db: Session = Depends(get_db)):
    # Verify existence first
    prog = db.query(MProgramacion).filter(MProgramacion.iMProgramacion == id).first()
    if not prog:
        raise HTTPException(status_code=404, detail=f"Programación {id} no encontrada")

    user_id = 1 
    date_to_use = request.date if request and request.date else None
    execution_ids = await execute_programacion_logic(db, id, ruc, manual_user_id=user_id, date_str=date_to_use)
    
    if not execution_ids:
        raise HTTPException(status_code=400, detail="No se generaron ejecuciones (verifique datos/programación)")

    return {"message": "Ejecución iniciada", "execution_ids": execution_ids}

class ExecuteManualRequest(BaseModel):
    date: str

@router.post("/sociedades/{ruc}/execute")
async def execute_sociedad_manual(ruc: str, request: ExecuteManualRequest, db: Session = Depends(get_db)):
    # Verify society exists
    sociedad = db.query(MSociedad).filter(MSociedad.tRuc == ruc).first()
    if not sociedad:
         raise HTTPException(status_code=404, detail=f"Sociedad {ruc} no encontrada")

    user_id = 1 # TODO:
    execution_ids = await execute_sociedad_logic(db, [ruc], manual_user_id=user_id, date_str=request.date)
    
    if not execution_ids:
        raise HTTPException(status_code=400, detail="No se generaron ejecuciones (verifique que la sociedad tenga cuenta SAP activa)")

    return {"message": "Ejecución iniciada", "execution_ids": execution_ids}

# Proveedores / Lista Blanca Endpoints

class ListaBlancaBase(BaseModel):
    tRucListaBlanca: str
    tRazonSocial: str
    lActivo: bool = True

class ListaBlancaResponse(ListaBlancaBase):
    fRegistro: datetime | None = None
    sociedades_rucs: List[str] = []
    sociedades_nombres: List[str] = []
    
    class Config:
        from_attributes = True

@router.get("/proveedores", response_model=List[ListaBlancaResponse])
def get_proveedores(db: Session = Depends(get_db)):
    proveedores = db.query(MListaBlanca).options(
        joinedload(MListaBlanca.sociedades).joinedload(MListaBlancaSociedad.sociedad)
    ).all()
    result = []
    for p in proveedores:
        sociedades = [s.tRucSociedad for s in p.sociedades]
        sociedades_nombres = [s.sociedad.tRazonSocial for s in p.sociedades if s.sociedad]
        p_dict = {
            "tRucListaBlanca": p.tRucListaBlanca,
            "tRazonSocial": p.tRazonSocial,
            "lActivo": p.lActivo,
            "fRegistro": p.fRegistro,
            "sociedades_rucs": sociedades,
            "sociedades_nombres": sociedades_nombres
        }
        result.append(p_dict)
    return result

class ListaBlancaSociedadesUpdate(BaseModel):
    sociedades: List[str]

@router.put("/proveedores/{ruc}/sociedades")
def update_proveedor_sociedades(ruc: str, update: ListaBlancaSociedadesUpdate, db: Session = Depends(get_db)):
    proveedor = db.query(MListaBlanca).filter(MListaBlanca.tRucListaBlanca == ruc).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    db.query(MListaBlancaSociedad).filter(MListaBlancaSociedad.tRucListaBlanca == ruc).delete()

    for sociedad_ruc in update.sociedades:
        new_relation = MListaBlancaSociedad(tRucListaBlanca=ruc, tRucSociedad=sociedad_ruc)
        db.add(new_relation)
    
    db.commit()
    return {"message": "Sociedades actualizadas correctamente"}

@router.post("/proveedores/preview")
async def preview_proveedores_excel(file: UploadFile = File(...)):
    if not file.filename.endswith('.xlsx') and not file.filename.endswith('.xls'):
        raise HTTPException(status_code=400, detail="Formato de archivo inválido. Solo se permiten archivos Excel (.xlsx, .xls)")
    
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        import unicodedata
        def normalize_str(s):
            return ''.join(c for c in unicodedata.normalize('NFD', str(s)) if unicodedata.category(c) != 'Mn').upper().strip()

        df.columns = [normalize_str(col) for col in df.columns]
        
        col_ruc = None
        col_razon = None
        
        for col in df.columns:
            if "RUC" in col:
                col_ruc = col
                break
        
        for col in df.columns:
            if "RAZON" in col or "SOCIAL" in col or "NOMBRE" in col:
                col_razon = col
                break
        
        if not col_ruc or not col_razon:
             raise HTTPException(status_code=400, detail=f"No se encontraron las columnas requeridas 'RUC' y 'RAZON SOCIAL' en el Excel.")
        
        preview_data = []
        df = df.fillna('')
        
        for i, row in df.iterrows():
            ruc = str(row[col_ruc]).strip()
            razon_social = str(row[col_razon]).strip()

            if ruc.endswith('.0'):
                ruc = ruc[:-2]

            import re
            ruc = re.sub(r'\D', '', ruc)

            if not ruc:
                continue
            
            preview_data.append({
                "id": i, 
                "ruc": ruc,
                "razonSocial": razon_social,
                "estado": True 
            })
            
        return preview_data
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error procesando excel: {e}")
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {str(e)}")

@router.delete("/proveedores/{ruc}")
def delete_proveedor(ruc: str, db: Session = Depends(get_db)):
    try:
        proveedor = db.query(MListaBlanca).filter(MListaBlanca.tRucListaBlanca == ruc).first()
        if not proveedor:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")
        
        db.delete(proveedor)
        db.commit()
        return {"message": "Proveedor eliminado correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar proveedor: {str(e)}")

@router.post("/proveedores/batch")
async def create_proveedores_batch(proveedores: List[ListaBlancaBase], db: Session = Depends(get_db)):
    try:
        count_created = 0
        count_updated = 0
        
        for prov in proveedores:
            existing = db.query(MListaBlanca).filter(MListaBlanca.tRucListaBlanca == prov.tRucListaBlanca).first()
            if existing:
                existing.tRazonSocial = prov.tRazonSocial
                existing.lActivo = prov.lActivo               
                existing.fModificacion = datetime.now()
                existing.iUsuarioModificacion = 1
                count_updated += 1
            else:
                new_prov = MListaBlanca(
                    tRucListaBlanca=prov.tRucListaBlanca,
                    tRazonSocial=prov.tRazonSocial,
                    lActivo=prov.lActivo,
                    fRegistro=datetime.now(),
                    iUsuarioRegistro=1
                )
                db.add(new_prov)
                count_created += 1
        
        db.commit()
        
        return {
            "message": "Proceso completado exitosamente",
            "created": count_created,
            "updated": count_updated
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error guardando datos: {str(e)}")

@router.post("/proveedores/upload")
async def upload_proveedores_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.xlsx') and not file.filename.endswith('.xls'):
        raise HTTPException(status_code=400, detail="Formato de archivo inválido. Solo se permiten archivos Excel (.xlsx, .xls)")
    
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        df.columns = [str(col).upper().strip() for col in df.columns]
        
        col_ruc = None
        col_razon = None
        
        for col in df.columns:
            if "RUC" in col:
                col_ruc = col
                break
        
        for col in df.columns:
            if "RAZON" in col or "SOCIAL" in col or "NOMBRE" in col:
                col_razon = col
                break
        
        if not col_ruc or not col_razon:
             raise HTTPException(status_code=400, detail=f"No se encontraron las columnas requeridas 'RUC' y 'RAZON SOCIAL' en el Excel.")
        
        count_created = 0
        count_updated = 0
        
        df = df.fillna('')
        
        for _, row in df.iterrows():
            ruc = str(row[col_ruc]).strip()
            razon_social = str(row[col_razon]).strip()
            
            if ruc.endswith('.0'):
                ruc = ruc[:-2]
            
            if not ruc or len(ruc) != 11 or not ruc.isdigit():
                continue
            
            existing = db.query(MListaBlanca).filter(MListaBlanca.tRucListaBlanca == ruc).first()
            if existing:
                existing.tRazonSocial = razon_social
                existing.fModificacion = datetime.now()
                existing.iUsuarioModificacion = 1
                count_updated += 1
            else:
                new_prov = MListaBlanca(
                    tRucListaBlanca=ruc,
                    tRazonSocial=razon_social,
                    lActivo=True,
                    fRegistro=datetime.now(),
                    iUsuarioRegistro=1
                )
                db.add(new_prov)
                count_created += 1
        
        db.commit()
        
        return {
            "message": "Proceso completado exitosamente",
            "created": count_created,
            "updated": count_updated
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error procesando excel: {e}")
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {str(e)}")
