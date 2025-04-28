from jose import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Callable, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from app.core.db import get_db
from jose.exceptions import JWTError
from app.models.models import Usuario
from passlib.context import CryptContext
import asyncio

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTOS = 30
REFRESH_TOKEN_EXPIRE_MINUTOS = 300
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def retry_operation(operation: Callable[[], Any], max_retries: int = 3, delay: float = 0.1):
    """Retry an async database operation with exponential backoff."""
    last_error = None
    for attempt in range(max_retries):
        try:
            return await operation()
        except OperationalError as e:
            last_error = e
            if attempt < max_retries - 1:
                await asyncio.sleep(delay * (2 ** attempt))
            continue
    raise last_error

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verificar_contraseña(contraseña: str, contraseña_encriptada: str) -> bool:
    return pwd_context.verify(contraseña, contraseña_encriptada)

def crear_token_acceso(datos: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = datos.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTOS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def crear_token_refresco(datos: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = datos.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTOS)
    to_encode.update({"exp": expire, "tipo": "refresco"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Usuario:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudo validar las credenciales"
            )

        async def get_user():
            result = await db.execute(select(Usuario).filter(Usuario.email == email))
            return result.scalar_one_or_none()

        usuario = await retry_operation(get_user)

        if usuario is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se pudo validar las credenciales"
            )

        return usuario

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar las credenciales"
        )

async def autenticar_usuario(db: AsyncSession, email: str, password: str) -> Optional[Usuario]:
    async def get_user():
        result = await db.execute(select(Usuario).filter(Usuario.email == email))
        return result.scalar_one_or_none()

    usuario = await retry_operation(get_user)
    
    if not usuario:
        return None
    if not verificar_contraseña(password, str(usuario.password)):
        return None
    return usuario

def crear_token_para_usuario(usuario: Usuario) -> dict:
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTOS)
    access_token = crear_token_acceso(
        datos={"sub": usuario.email, "tipo": "acceso"},
        expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTOS)
    refresh_token = crear_token_refresco(
        datos={"sub": usuario.email},
        expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
