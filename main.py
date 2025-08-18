# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import os

from database import engine, Base, get_db
import models, schemas, auth

# Cria tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== JWT por variáveis de ambiente =====
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")  # defina no Render!
JWT_ALG = os.getenv("JWT_ALG", "HS256")
JWT_EXP_MIN = int(os.getenv("JWT_EXP_MIN", "4320"))  # 3 dias

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_jwt(sub: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=JWT_EXP_MIN)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def decode_jwt(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])

def verificar_token(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = decode_jwt(token)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
def get_current_user(db: Session = Depends(get_db),
                     token: str = Depends(oauth2_scheme)) -> models.Usuario:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return user

# ================= ROTAS =================

@app.post("/usuario", response_model=schemas.UsuarioResponse)
def criar_usuario(user: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    if auth.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    novo = models.Usuario(
        nome=user.nome,
        cpf=user.cpf,
        nome_usuario=user.nome_usuario,
        email=user.email,
        senha=auth.get_password_hash(user.senha),
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

@app.post("/login")
def login(login_data: schemas.Login, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, login_data.email, login_data.senha)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    token = create_jwt(user.email)
    return {"access_token": token, "token_type": "bearer"}

# ---- Leituras (CRUD simples) ----

@app.post("/leituras", response_model=schemas.LeituraResponse)
def criar_leitura(payload: schemas.LeituraCreate,
                  db: Session = Depends(get_db),
                  user: models.Usuario = Depends(get_current_user)):
    status = payload.status or ("PERIGO" if payload.ppm >= 400 else "SEGURO")
    leitura = models.Leitura(
        ppm=payload.ppm,
        status=status,
        origem=payload.origem,
        user_id=user.id
    )
    db.add(leitura)
    db.commit()
    db.refresh(leitura)
    return leitura

@app.get("/leituras", response_model=list[schemas.LeituraResponse])
def listar_leituras(limit: int = 100,
                    db: Session = Depends(get_db),
                    user: models.Usuario = Depends(get_current_user)):
    return (
        db.query(models.Leitura)
          .filter(models.Leitura.user_id == user.id)
          .order_by(models.Leitura.created_at.desc())   # <- created_at
          .limit(limit)
          .all()
    )



@app.get("/dashboard")
def acessar_dashboard(email: str = Depends(verificar_token)):
    return {"mensagem": f"Bem-vindo, {email}. Dados protegidos acessados com sucesso."}

@app.get("/")
def raiz():
    return {"status": "API rodando com sucesso!"}
# main.py
@app.get("/health")
def health():
    return {"ok": True}
