import asyncio
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import MProgramacion
from app.services.execution import execute_programacion_logic

logger = logging.getLogger(__name__)

executed_schedules = set()

async def check_schedules():
    """
    Periodically checks for schedules to run.
    """
    logger.info("Scheduler started.")
    while True:
        try:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            current_day_name = now.strftime("%A")
            days_map = {
                "Monday": ["Lun", "Lunes", "Mo"],
                "Tuesday": ["Mar", "Martes", "Tu"],
                "Wednesday": ["Mie", "Mié", "Miercoles", "Miércoles", "We"],
                "Thursday": ["Jue", "Jueves", "Th"],
                "Friday": ["Vie", "Viernes", "Fr"],
                "Saturday": ["Sab", "Sábado", "Sa"],
                "Sunday": ["Dom", "Domingo", "Su"]
            }
            
            possible_day_names = days_map.get(current_day_name, [])
            
            db = SessionLocal()
            try:
                programaciones = db.query(MProgramacion).filter(MProgramacion.lActivo == True).all()
                for prog in programaciones:
                    if prog.tHora != current_time:
                        continue
                    match_day = False
                    if not prog.tDias:
                        continue
                        
                    prog_days = [d.strip() for d in prog.tDias.split(',')]
                    for pd in prog_days:
                        if pd in possible_day_names:
                            match_day = True
                            break
                    
                    if not match_day:
                        continue

                    today_str = now.strftime("%Y-%m-%d")
                    cache_key = (prog.iMProgramacion, today_str)
                    
                    if cache_key in executed_schedules:
                        continue

                    logger.info(f"Executing schedule {prog.iMProgramacion} - {prog.tNombre}")
                    await execute_programacion_logic(db, prog.iMProgramacion)              
                    executed_schedules.add(cache_key)
                    
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in scheduler loop: {e}")

        await asyncio.sleep(60)

def start_scheduler():
    asyncio.create_task(check_schedules())
