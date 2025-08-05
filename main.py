from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from database import engine, Base, get_db
import models, schemas, auth

# Criar tabelas no banco caso não existam
Base.metadata.create_all(bind=engine)

# Inicializa FastAPI
app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Pode restringir para domínios específicos depois
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
    # Verifica se já existe email
    db_user = auth.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    # Cria objeto de usuário
    novo_usuario = models.Usuario(
        nome=user.nome,
        cpf=user.cpf,
        nome_usuario=user.nome_usuario,
        email=user.email,
        senha=auth.get_password_hash(user.senha)  # Criptografa senha
    )

    # Salva no banco
    db.add(novo_usuario)
    db.commit()       # Salva as alterações
    db.refresh(novo_usuario)  # Atualiza objeto com ID gerado

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
