from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.models import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioRead
from app.crud.crud_usuario import *
from app.core.security import *
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"]  # This helps organize the API documentation
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


