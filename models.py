# models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime, timezone
from database import Base
from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cpf = Column(String, unique=True, index=True, nullable=False)
    nome_usuario = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha = Column(String, nullable=False)


class Leitura(Base):
    __tablename__ = "leituras"

    id = Column(Integer, primary_key=True, index=True)
    ppm = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    origem = Column(String, nullable=True)

    # salva no horário de Brasília (GMT-3)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone(timedelta(hours=-3))),
        nullable=False
    )

    # vincula ao usuário
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
