from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal, engine, Base, get_db
import models, schemas, auth

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.post("/usuario")
def criar_usuario(user: schemas.UsuarioCreate, db=Depends(get_db)):
    db_user = auth.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    return auth.create_user(db, user)

@app.post("/login")
def login(login_data: schemas.Login, db=Depends(get_db)):
    user = auth.authenticate_user(db, login_data.email, login_data.senha)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    token = auth.create_jwt(user.email)
    return {"access_token": token}
