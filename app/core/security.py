from jose import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.db import get_db
from jose.exceptions import JWTError
from app.models.models import Usuario
from passlib.context import CryptContext

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTOS = 30
REFRESH_TOKEN_EXPIRE_MINUTOS = 300  # 5 horas
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Encripta la contraseña proporcionada utilizando el algoritmo bcrypt.
    
    Args:
        password (str): La contraseña proporcionada por el usuario.
    
    Returns:
        str: La contraseña encriptada.
    """
    return pwd_context.hash(password)

def verificar_contraseña(contraseña: str, contraseña_encriptada: str) -> bool:
    """
    Verifica si la contraseña proporcionada coincide con la contraseña encriptada almacenada.
    
    Args:
        contraseña (str): La contraseña proporcionada por el usuario.
        contraseña_encriptada (str): La contraseña encriptada almacenada en la base de datos.
    
    Returns:
        bool: True si la contraseña coincide, False en caso contrario.
    """
    return pwd_context.verify(contraseña, contraseña_encriptada)

def crear_token_acceso(datos: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token de acceso JWT con la información proporcionada.
    
    Args:
        datos (dict): Diccionario con la información que se quiere incluir en el token.
        expires_delta (Optional[timedelta], optional): Tiempo de expiración del token. Defaults to None.
    
    Returns:
        str: El token de acceso JWT.
    """
    to_encode = datos.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTOS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def crear_token_refresco(datos: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token de refresco JWT con la información proporcionada.

    Args:
        datos (dict): Diccionario con la información que se quiere incluir en el token.
        expires_delta (Optional[timedelta], optional): Tiempo de expiración del token. Si no se proporciona, se usará el tiempo de expiración por defecto.

    Returns:
        str: El token de refresco JWT.
    """

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
    """
    Obtiene el usuario actual autenticado a partir de un token JWT proporcionado.

    Args:
        token (str): Token de acceso JWT del usuario, inyectado automáticamente por FastAPI.
        db (AsyncSession): Sesión asincrónica de la base de datos, inyectada por FastAPI.

    Returns:
        Usuario: Instancia del usuario autenticado.

    Raises:
        HTTPException: Si el token es inválido o no se puede validar, o si el usuario no se encuentra en la base de datos.
    """

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="No se pudo validar las credenciales"
            )

        result = await db.execute(select(Usuario).filter(Usuario.email == email))
        usuario = result.scalar_one_or_none()

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
    """
    Autentica un usuario verificando su email y contraseña.

    Args:
        db (AsyncSession): Sesión asincrónica de la base de datos.
        email (str): Correo electrónico del usuario.
        password (str): Contraseña del usuario.

    Returns:
        Optional[Usuario]: El usuario autenticado si las credenciales son correctas, 
        de lo contrario, None.
    """

    result = await db.execute(select(Usuario).filter(Usuario.email == email))
    usuario = result.scalar_one_or_none()
    if not usuario:
        return None
    if not verificar_contraseña(password, str(usuario.password)): 
        return None
    return usuario

def crear_token_para_usuario(usuario: Usuario) -> dict:
    """
    Crea un token de acceso y un token de refresco para un usuario.

    Args:
        usuario (Usuario): Instancia del usuario para el que se crean los tokens.

    Returns:
        dict: Diccionario con los tokens de acceso y refresco, y el tipo de token.
    """
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
