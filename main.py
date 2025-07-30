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
        raise HTTPException(status_code=400, detail="Email ja cadastrado")
    return auth.create_user(db, user)

@app.post("/login")
def login(login_data: schemas.Login, db=Depends(get_db)):
    user = auth.authenticate_user(db, login_data.email, login_data.senha)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais invalidas")
    token = auth.create_jwt(user.email)
    return {"access_token": token}
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

SECRET = "segredo_super_forte"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verificar_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token invalido")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalido")

@app.get("/dashboard")
def acessar_dashboard(email: str = Depends(verificar_token)):
    return {"mensagem": f"Bem-vindo, {email}. Dados protegidos acessados com sucesso."}
@app.get("/")
def raiz():
    return {"status": "API rodando com sucesso!"}
