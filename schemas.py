from pydantic import BaseModel

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
