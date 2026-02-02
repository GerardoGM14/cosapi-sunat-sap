import sys
import os
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.database import SessionLocal
from app.services.execution import execute_sociedad_logic

async def test_exec():
    db = SessionLocal()
    try:
        ruc = "20100082391"
        print(f"Testing execution logic for RUC: {ruc}")
        # We don't actually want to run the bot (it spawns subprocess), 
        # but we want to see what logic it follows.
        # Since execute_sociedad_logic calls run_bot_logic which calls subprocess, 
        # we might want to mock run_bot_logic or just let it fail/run and check logs.
        # But wait, execute_sociedad_logic prepares the config.
        # Let's verify the data fetching part by extracting it or running a modified version.
        
        # Let's just query the object using the SAME logic as execution.py
        from app.models import MSociedad
        sociedad = db.query(MSociedad).filter(MSociedad.tRuc == ruc).first()
        
        if sociedad:
            print(f"Sociedad found: {sociedad.tRazonSocial}")
            print(f"tCodigoSap: '{sociedad.tCodigoSap}'")
            print(f"tRazonSocial: '{sociedad.tRazonSocial}'")
            
            soc_code = sociedad.tCodigoSap or sociedad.tRazonSocial
            print(f"Calculated soc_code: '{soc_code}'")
            
            if soc_code == 'PE02':
                print("Logic is CORRECT. It resolves to PE02.")
            else:
                print(f"Logic is INCORRECT. It resolves to {soc_code}.")
        else:
            print("Sociedad not found in DB.")
            
    finally:
        db.close()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_exec())
