from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.models import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioRead, TokenRefreshRequest
from app.crud.crud_usuario import *
from app.core.security import *
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import timedelta

router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"] 
)
@router.get("/me", response_model=UsuarioRead)
def get_current_user(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    return usuario_actual

@router.post("/", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def crear_usuario_endpoint(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        return crear_usuario(usuario, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{usuario_id}", response_model=UsuarioRead)
def get_usuario(usuario_id: int, db: Session = Depends(get_db)):
    try:
        return obtener_usuario(usuario_id, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/{usuario_id}", response_model=UsuarioRead)
def update_usuario_endpoint(usuario_id: int, usuario: UsuarioUpdate, db: Session = Depends(get_db)):
    try:
        return update_usuario(usuario_id, usuario, db) 
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)      
        )

@router.post("/login", response_model=dict)
async def login_para_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        usuario = autenticar_usuario(db, form_data.username, form_data.password)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return crear_token_para_usuario(usuario)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/refresh", response_model=dict)
async def refrescar_token_acceso(
    refresh_request: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Refresca el token de acceso utilizando un token de refresco válido.
    """
    token_refresco = refresh_request.refresh_token
    try:
        payload = jwt.decode(token_refresco, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        token_type: str | None = payload.get("tipo")

        if email is None or token_type != "refresco":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de refresco inválido o caducado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verificar si el usuario existe (opcional pero recomendado)
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        if usuario is None:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Crear un nuevo token de acceso
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTOS)
        nuevo_access_token = crear_token_acceso(
            datos={"sub": usuario.email, "tipo": "acceso"},
            expires_delta=access_token_expires
        )
        return {"access_token": nuevo_access_token, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresco inválido o caducado",
            headers={"WWW-Authenticate": "Bearer"},
        )
