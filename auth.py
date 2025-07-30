from models import Usuario
from schemas import UsuarioCreate
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
import datetime

SECRET = "segredo_super_forte"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()

def create_user(db: Session, user: UsuarioCreate):
    hashed = pwd_context.hash(user.senha)
    db_user = Usuario(email=user.email, senha=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, senha: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not pwd_context.verify(senha, user.senha):
        return False
    return user

def create_jwt(email: str):
    exp = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    to_encode = {"sub": email, "exp": exp}
    return jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
