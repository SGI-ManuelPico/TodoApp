from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.models.models import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioRead, TokenRefreshRequest, Token
from app.crud.crud_usuario import *
from app.core.security import *
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from app.core.limiter import limiter

router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"] 
)

@router.get("/me", response_model=UsuarioRead)
async def get_current_user(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    """
    Obtiene el usuario actual autenticado.
    """
    return usuario_actual

@router.post("/", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
async def crear_usuario_endpoint(usuario: UsuarioCreate, db: AsyncSession = Depends(get_db)):
    """
    Crea un nuevo usuario.
    """
    
    try:
        return await crear_usuario(usuario, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{usuario_id}", response_model=UsuarioRead)
async def get_usuario(usuario_id: int, db: AsyncSession = Depends(get_db)):
    """
    Obtiene un usuario específico por su ID.
    
    Args:
    - usuario_id (int): ID del usuario a obtener.
    
    Raises:
    - HTTPException: 404 si el usuario no existe.
    """
    try:
        return await obtener_usuario(usuario_id, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/{usuario_id}", response_model=UsuarioRead)
async def update_usuario_endpoint(usuario_id: int, usuario: UsuarioUpdate, db: AsyncSession = Depends(get_db)):
    """
    Actualiza un usuario específico por su ID.
    
    Args:
        usuario_id (int): ID del usuario a actualizar.
        usuario (UsuarioUpdate): Datos del usuario a actualizar.
    
    Raises:
        HTTPException: 404 si el usuario no existe.
    """
    try:
        return await update_usuario(usuario_id, usuario, db) 
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)      
        )

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login_para_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Autentica un usuario utilizando un formulario de inicio de sesión y devuelve tokens JWT.
    Rate limit: 5 intentos por minuto por dirección IP.
    
    Args:
    - form_data (OAuth2PasswordRequestForm): Formulario de inicio de sesión.
    - db (AsyncSession): Sesión de la base de datos.
    - auth_service (AuthService): Servicio de autenticación.
    
    Returns:
    - Token: Token de acceso y refresco JWT.
    
    Raises:
    - HTTPException: 401 si el usuario no existe o la contraseña es incorrecta.
    - HTTPException: 429 si se excede el límite de intentos.
    """
    try:
        usuario = await auth_service.authenticate_user(form_data.username, form_data.password)
        return await auth_service.create_tokens_for_user(usuario)
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/refresh", response_model=Token)
@limiter.limit("10/minute")
async def refrescar_token_acceso(
    request: Request,
    refresh_request: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Refresca el token de acceso utilizando un token de refresco válido.
    Rate limit: 10 intentos por minuto por dirección IP.
    """
    try:
        payload = await auth_service.token_manager.verify_token(refresh_request.refresh_token, db)
        if payload.type != "refresh":
            raise InvalidCredentialsError("Invalid refresh token type")

        user = await auth_service._get_user_by_email(email=payload.sub)
        if not user:
            raise InvalidCredentialsError("User not found")

        return await auth_service.create_tokens_for_user(user)

    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/logout", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def logout_endpoint(
    request: Request,
    current_user: Usuario = Depends(obtener_usuario_actual),
    auth_service: AuthService = Depends(get_auth_service),
    token: str = Depends(oauth2_scheme)
):
    """
    Cierra la sesión del usuario actual invalidando sus tokens.
    Rate limit: 10 intentos por minuto por dirección IP.

    Args:
    - current_user (Usuario): Usuario autenticado actual.
    - auth_service (AuthService): Servicio de autenticación.
    - token (str): Token de acceso actual.

    Returns:
    - dict: Mensaje de confirmación.

    Raises:
    - HTTPException: 401 si el token es inválido.
    """
    try:
        # Llama al método logout simplificado, pasando solo el token de acceso
        await auth_service.logout(token) 
        return {"detail": "Sesión cerrada correctamente"}
    except AuthenticationError as e:
        # Captura errores de autenticación (ej. token inválido, ya revocado)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
