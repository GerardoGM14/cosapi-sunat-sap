from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add backend to path to import models if needed, but direct SQL is easier for checking
sys.path.append(os.path.join(os.getcwd(), 'backend'))

SQLALCHEMY_DATABASE_URL = "sqlite:///backend/cosapi.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_cosapi_code():
    db = SessionLocal()
    try:
        # Note: In MSociedad model, PK is tRuc, not iMSociedad.
        # Let's select tRuc, tRazonSocial, tCodigoSap
        result = db.execute(text("SELECT tRuc, tRazonSocial, tCodigoSap FROM MSociedad WHERE tRazonSocial LIKE '%COSAPI S.A%'"))
        rows = result.fetchall()
        print(f"Found {len(rows)} rows:")
        for row in rows:
            print(f"RUC: {row[0]}, RazonSocial: {row[1]}, CodigoSap: {row[2]}")
            
            # If code is missing, let's update it to PE02 as user mentioned
            if 'COSAPI S.A' in row[1] and not row[2]:
                print(f"Updating CodigoSap for {row[1]} to PE02...")
                db.execute(text("UPDATE MSociedad SET tCodigoSap = 'PE02' WHERE tRuc = :ruc"), {"ruc": row[0]})
                db.commit()
                print("Update committed.")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_cosapi_code()
