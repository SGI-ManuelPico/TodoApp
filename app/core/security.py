from pydantic import BaseModel, field_validator
from datetime import datetime, timedelta, timezone
from typing import Optional, Callable, Any, Literal, TypeVar
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.exc import OperationalError
from app.core.db import get_db
from jose.exceptions import JWTError
from jose import jwt
from app.models.models import Usuario, BlacklistedToken
from passlib.context import CryptContext
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

# Actualizar la configuración de CryptContext para la última versión de bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
    bcrypt__default_rounds=12
)

class Settings(BaseModel):
    SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 300
    
    class Config:
        from_attributes = True

settings = Settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/login")

# Custom Exceptions
class AuthenticationError(Exception):
    """Base para todas las excepciones de autenticación"""
    pass

class InvalidCredentialsError(AuthenticationError):
    """Credenciales inválidas"""
    pass

class TokenExpiredError(AuthenticationError):
    """Token ha expirado"""
    pass

# Token Types and Payload Schema
TokenType = Literal["access", "refresh"]
UserT = TypeVar("UserT", bound=Usuario)

class TokenPayload(BaseModel):
    sub: str
    exp: datetime
    type: TokenType

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: int(dt.timestamp())
        }

    @field_validator('exp', mode='before')
    @classmethod
    def validate_exp(cls, v):
        if isinstance(v, (int, float)):
            return datetime.fromtimestamp(v, tz=timezone.utc)
        return v

# Password Management
class PasswordManager:
    def __init__(self, context: CryptContext):
        self.context = context
    
    def hash_password(self, password: str) -> str:
        return self.context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.context.verify(plain_password, hashed_password)

# Token Blacklist
class TokenBlacklist:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def is_blacklisted(self, token: str) -> bool:
        """Verifica si un token esta en la blacklist"""
        result = await self.db.execute(
            select(BlacklistedToken).filter(BlacklistedToken.token == token)
        )
        return result.scalar_one_or_none() is not None

    async def blacklist_token(self, token: str, expires_at: datetime):
        """Agrega un token a la blacklist"""
        blacklisted_token = BlacklistedToken(
            token=token,
            expires_at=expires_at
        )
        self.db.add(blacklisted_token)
        await self.db.commit()

    async def cleanup_expired_tokens(self):
        """Remueve tokens expirados de la blacklist"""
        now = datetime.now(timezone.utc)
        await self.db.execute(
            delete(BlacklistedToken).where(BlacklistedToken.expires_at < now)
        )
        await self.db.commit()

# Manejo de Tokens
class TokenManager:
    def __init__(self, secret_key: str, algorithm: str):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def create_token(
        self,
        subject: str,
        token_type: TokenType,
        expires_delta: timedelta
    ) -> tuple[str, datetime]:
        expire = datetime.now(timezone.utc) + expires_delta
        payload = TokenPayload(
            sub=subject,
            exp=expire,
            type=token_type
        )
        # Convertimos a un diccionario para serializarlo a JSON
        payload_dict = payload.model_dump() 
        token = jwt.encode(payload_dict, self.secret_key, self.algorithm)
        return token, expire

    async def verify_token(
        self,
        token: str,
        db: AsyncSession
    ) -> TokenPayload:
        try:
            # Primero verificamos si el token está en la blacklist
            blacklist = TokenBlacklist(db)
            if await blacklist.is_blacklisted(token):
                raise InvalidCredentialsError("El token ha sido revocado")

            # Luego decodificamos el token y verificamos la firma
            payload = jwt.decode(token, self.secret_key, [self.algorithm])
            
            # convertimos el campo 'exp' a un objeto datetime
            payload['exp'] = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
            
            return TokenPayload(**payload)
        except JWTError:
            raise InvalidCredentialsError("Token invalido")

# Authentication Service
class AuthService:
    def __init__(
        self,
        token_manager: TokenManager,
        password_manager: PasswordManager,
        db: AsyncSession
    ):
        self.token_manager = token_manager
        self.password_manager = password_manager
        self.db = db
        self.blacklist = TokenBlacklist(db)

    async def authenticate_user(
        self,
        email: str,
        password: str
    ) -> Usuario:
        user = await self._get_user_by_email(email)
        if not user:
            raise InvalidCredentialsError("Invalid email or password")
        
        if not self.password_manager.verify_password(password, user.password):
            raise InvalidCredentialsError("Invalid email or password")
            
        return user
    
    async def create_tokens_for_user(self, user: Usuario) -> dict:
        access_token, access_exp = self.token_manager.create_token(
            subject=user.email,
            token_type="access",
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        refresh_token, refresh_exp = self.token_manager.create_token(
            subject=user.email,
            token_type="refresh",
            expires_delta=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    async def logout(self, access_token: str):
        """Blacklist the access token"""
        # Verify access token and get payload to determine expiration for blacklist entry
        payload = await self.token_manager.verify_token(access_token, self.db)
        # Use the exp attribute directly as it's already a datetime object
        await self.blacklist.blacklist_token(access_token, payload.exp)

        # Cleanup expired tokens periodically (can still be useful)
        await self.blacklist.cleanup_expired_tokens()

    async def _get_user_by_email(self, email: str) -> Optional[Usuario]:
        result = await self.db.execute(select(Usuario).filter(Usuario.email == email))
        return result.scalar_one_or_none()

# Dependency Injection
async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    token_manager = TokenManager(settings.SECRET_KEY, settings.ALGORITHM)
    password_manager = PasswordManager(pwd_context)
    return AuthService(token_manager, password_manager, db)

# Utility Functions
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

# Legacy function names for backward compatibility
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verificar_contraseña(contraseña: str, contraseña_encriptada: str) -> bool:
    return pwd_context.verify(contraseña, contraseña_encriptada)

# JWT Token Functions
def crear_token_acceso(datos: dict, expires_delta: Optional[timedelta] = None) -> str:
    token_manager = TokenManager(settings.SECRET_KEY, settings.ALGORITHM)
    token, _ = token_manager.create_token(
        subject=datos["sub"],
        token_type="access",
        expires_delta=expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return token

def crear_token_refresco(datos: dict, expires_delta: Optional[timedelta] = None) -> str:
    token_manager = TokenManager(settings.SECRET_KEY, settings.ALGORITHM)
    token, _ = token_manager.create_token(
        subject=datos["sub"],
        token_type="refresh",
        expires_delta=expires_delta or timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    )
    return token

# Current User Dependency
async def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> Usuario:
    try:
        payload = await auth_service.token_manager.verify_token(token, db)
        email = payload.sub
        
        if not email:
            raise InvalidCredentialsError("Invalid token payload")

        user = await auth_service._get_user_by_email(email)
        if not user:
            raise InvalidCredentialsError("User not found")

        return user

    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

# Authentication Functions
async def autenticar_usuario(
    db: AsyncSession,
    email: str,
    password: str,
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[Usuario]:
    try:
        return await auth_service.authenticate_user(db, email, password)
    except AuthenticationError:
        return None

def crear_token_para_usuario(
    usuario: Usuario,
    auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    return auth_service.create_tokens_for_user(usuario)
