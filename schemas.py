from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class UsuarioCreate(BaseModel):
    nome: str
    cpf: str
    nome_usuario: str
    email: str
    senha: str


class Login(BaseModel):
    email: str
    senha: str
    
class UsuarioResponse(BaseModel):
    id: int
    nome: str
    cpf: str
    nome_usuario: str
    email: str

    class Config:
        from_attributes = True
# NOVOS:
class LeituraCreate(BaseModel):
    ppm: int
    status: Optional[str] = None
    origem: Optional[str] = "android"

class LeituraResponse(BaseModel):
    id: int
    ppm: int
    status: str
    origem: str | None
    created_at: datetime = Field(alias="criado_em")

    class Config:
        populate_by_name = True
