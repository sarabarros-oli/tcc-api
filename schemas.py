from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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
    origem: Optional[str] = "pico"  

class LeituraResponse(BaseModel):
    id: int
    ppm: int
    status: str
    origem: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True