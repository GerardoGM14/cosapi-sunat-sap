from sqlalchemy.orm import Session
from datetime import datetime
from app.models import MProgramacion, MProgramacionSociedad, MSociedad, MSap, MSapSociedad, DEjecucion
from app.api.bot import run_bot_logic, BotConfig, SunatConfig, SapConfig, GeneralConfig
import logging

logger = logging.getLogger(__name__)

async def execute_programacion_logic(db: Session, programacion_id: int, ruc: str | None = None, manual_user_id: int | None = None):
    prog = db.query(MProgramacion).filter(MProgramacion.iMProgramacion == programacion_id).first()
    if not prog:
        logger.error(f"Programación {programacion_id} no encontrada")
        return []

    target_rucs = []
    if ruc:
        target_rucs = [ruc]
    else:
        rels = db.query(MProgramacionSociedad).filter(MProgramacionSociedad.iMProgramacion == programacion_id).all()
        target_rucs = [r.tRuc for r in rels]
        
    return await execute_sociedad_logic(db, target_rucs, manual_user_id)

async def execute_sociedad_logic(db: Session, target_rucs: list[str], manual_user_id: int | None = None, date_str: str | None = None):
    created_executions = []

    if not date_str:
        date_str = datetime.now().strftime("%d/%m/%Y")

    for target_ruc in target_rucs:
        try:
            sociedad = db.query(MSociedad).filter(MSociedad.tRuc == target_ruc).first()
            if not sociedad:
                logger.warning(f"Sociedad {target_ruc} no encontrada, saltando...")
                continue

            sap_rel = db.query(MSapSociedad).filter(
                MSapSociedad.tRuc == target_ruc, 
                MSapSociedad.lActivo == True
            ).first()
            
            sap_account = None
            if sap_rel:
                sap_account = db.query(MSap).filter(MSap.iMSAP == sap_rel.iMSAP).first()
                
            if not sap_account:
                logger.warning(f"No hay cuenta SAP activa asociada a {target_ruc}, saltando...")
                continue

            new_exec = DEjecucion(
                tTipo='M' if manual_user_id else 'A',
                tRuc=target_ruc,
                iMSAP=sap_account.iMSAP,
                fRegistro=datetime.utcnow(),
                iUsuarioEjecucion=manual_user_id,
            )
            db.add(new_exec)
            db.commit()
            db.refresh(new_exec)
            created_executions.append(new_exec.iMEjecucion)

            sunat_user = sociedad.tUsuario or ""
            sunat_pass = sociedad.tClave or ""
            sap_user = sap_account.tUsuario or ""
            sap_pass = sap_account.tClave or ""
            soc_code = sociedad.tCodigoSap or sociedad.tRazonSocial 

            try:
                dt_obj = datetime.strptime(date_str, "%d/%m/%Y")
                date_suffix = dt_obj.strftime("%d%m%y")
            except:
                date_suffix = datetime.now().strftime("%d%m%y")
                
            folder_name = f"{soc_code}_{date_suffix}"
            base_download_dir = "/home/sertech/sunat-sap" 
            full_folder_path = f"{base_download_dir}/{folder_name}"

            config = BotConfig(
                sunat=SunatConfig(
                    ruc=target_ruc,
                    usuario=sunat_user,
                    claveSol=sunat_pass
                ),
                sap=SapConfig(
                    usuario=sap_user,
                    password=sap_pass
                ),
                general=GeneralConfig(
                    sociedad=soc_code,
                    fecha=date_str,
                    folder=full_folder_path
                ),
                execution_id=new_exec.iMEjecucion
            )
            await run_bot_logic(config)
            
        except Exception as e:
            logger.error(f"Error executing for RUC {target_ruc}: {e}")
            
    return created_executions
