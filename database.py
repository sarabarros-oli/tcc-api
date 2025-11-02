from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
from database import Base, engine  # seu arquivo que tem engine e Base
import models  # todos os modelos que você criou

# Cria as tabelas no banco, caso não existam
Base.metadata.create_all(bind=engine)


DATABASE_URL ="postgresql://postgres:teDzZWkVFmoqSeIiDHtoiOnCeXmTmaDW@interchange.proxy.rlwy.net:23383/railway"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
