from passlib.context import CryptContext
from models import Usuario
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()

def create_user(db: Session, user_data):
    hashed_password = pwd_context.hash(user_data.senha)  
    novo_usuario = Usuario(
        nome=user_data.nome,
        cpf=user_data.cpf,
        nome_usuario=user_data.nome_usuario,
        email=user_data.email,
        senha=hashed_password
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario

def authenticate_user(db: Session, email: str, senha: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not pwd_context.verify(senha, user.senha):
        return False
    return user

from jose import jwt
import datetime

SECRET = "segredo_super_forte"
ALGORITHM = "HS256"

def create_jwt(email: str):
    exp = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    to_encode = {"sub": email, "exp": exp}
    return jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
