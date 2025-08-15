from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os
from database import engine, Base, get_db
import models, schemas, auth
from sqlalchemy import create_engine
from database import Base
from typing import List


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurações JWT
SECRET = "segredo_super_forte"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ---------------- ROTAS ----------------
print(schemas.UsuarioCreate.model_json_schema())
@app.post("/usuario", response_model=schemas.UsuarioResponse)
def criar_usuario(user: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    # Verifica se ja existe email
    db_user = auth.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    # Cria objeto de usuario
    novo_usuario = models.Usuario(
        nome=user.nome,
        cpf=user.cpf,
        nome_usuario=user.nome_usuario,
        email=user.email,
        senha=auth.get_password_hash(user.senha)  # Criptografa senha
    )

   
    db.add(novo_usuario)
    db.commit()       
    db.refresh(novo_usuario)  

    return novo_usuario




@app.post("/login")
def login(login_data: schemas.Login, db: Session = Depends(get_db)):
    """Realiza login e retorna token JWT"""
    user = auth.authenticate_user(db, login_data.email, login_data.senha)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    token = auth.create_jwt(user.email)
    return {"access_token": token}


def verificar_token(token: str = Depends(oauth2_scheme)):
    """Valida o token JWT"""
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# ========= NOVO: criar leitura =========

# ========== CRIA LEITURA ==========
@app.post("/leituras", response_model=schemas.LeituraResponse)
def criar_leitura(payload: schemas.LeituraCreate, db: Session = Depends(get_db)):
    status = payload.status or ("PERIGO" if payload.ppm >= 400 else "SEGURO")
    leitura = models.Leitura(ppm=payload.ppm, status=status, origem=payload.origem)
    db.add(leitura)
    db.commit()
    db.refresh(leitura)
    return leitura

# ========== LISTA LEITURAS ==========
@app.get("/leituras", response_model=List[schemas.LeituraResponse])
def listar_leituras(
    limit: int = 100,
    db: Session = Depends(get_db),
    email: str = Depends(verificar_token),   # protegido por JWT
):
    return (
        db.query(models.Leitura)
        .order_by(models.Leitura.criado_em.desc())
        .limit(limit)
        .all()
    )

# ========= NOVO: listar histórico do banco =========
@app.get("/historico", response_model=List[schemas.LeituraResponse])
def listar_historico(
    limit: int = 100,
    db: Session = Depends(get_db),
    email: str = Depends(verificar_token)  # protege com JWT (igual /dashboard)
):
    return db.query(models.Leitura)\
             .order_by(models.Leitura.created_at.desc())\
             .limit(limit).all()

@app.get("/dashboard")
def acessar_dashboard(email: str = Depends(verificar_token)):
    """Endpoint protegido"""
    return {"mensagem": f"Bem-vindo, {email}. Dados protegidos acessados com sucesso."}


@app.get("/")
def raiz():
    """Rota raiz para teste"""
    return {"status": "API rodando com sucesso!"}


historico_data = [
    {"data": "2025-07-30", "ppm": 340},
    {"data": "2025-07-29", "ppm": 280},
    {"data": "2025-07-28", "ppm": 310},
]

@app.get("/historico")
def get_historico(email: str = Depends(verificar_token)):
    """Retorna histórico fictício de leituras"""
    return historico_data
