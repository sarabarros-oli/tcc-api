from sqlalchemy import Column, Integer, String
from database import Base
from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime, timezone


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cpf = Column(String, nullable=False)
    nome_usuario = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha = Column(String, nullable=False)

class Leitura(Base):
    __tablename__ = "leituras"
    id = Column(Integer, primary_key=True, index=True)
    ppm = Column(Integer, nullable=False)
    status = Column(String, nullable=False)      # "SEGURO" | "PERIGO"
    origem = Column(String, nullable=True)       # ex: "pico2w" / "sala1"
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)