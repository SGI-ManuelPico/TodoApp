from jose import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.db import get_db
from jose.exceptions import JWTError
from app.models.models import Usuario
from passlib.context import CryptContext

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTOS = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Encripta una contraseña utilizando bcrypt.
    """
    return pwd_context.hash(password)

def verificar_contraseña(contraseña: str, contraseña_encriptada: str) -> bool:
    """
    Verifica si una contraseña coincide con una contraseña encriptada utilizando bcrypt.
    """
    return pwd_context.verify(contraseña, contraseña_encriptada)


def crear_token_acceso(datos: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token de acceso JWT con los datos proporcionados y una duración de expiración opcional.
    """
    to_encode = datos.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTOS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def obtener_usuario_actual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    """
    Obtiene el usuario actual a partir del token JWT proporcionado.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id: int | None = payload.get("sub")  # Allow None in type hint

        if usuario_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No se pudo validar las credenciales")

        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

        if usuario is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No se pudo validar las credenciales")

        return usuario

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No se pudo validar las credenciales")


def autenticar_usuario(db: Session, email: str, password: str) -> Optional[Usuario]:
    """
    Autentica un usuario verificando su email y contraseña.
    Retorna el usuario si es válido, None si no lo es.
    """
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return None
    if not verificar_contraseña(password, str(usuario.password)): 
        return None
    return usuario

def crear_token_para_usuario(usuario: Usuario) -> dict:
    """
    Crea un token de acceso para un usuario específico.
    Retorna un diccionario con el token y su tipo.
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTOS)
    access_token = crear_token_acceso(
        datos={"sub": str(usuario.id)}, 
        expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
