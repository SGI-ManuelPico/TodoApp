from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.models import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioRead
from app.crud.crud_usuario import *

router = APIRouter()

@router.post("/usuarios", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def crear_usuario_endpoint(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        return crear_usuario(usuario, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/usuarios/{usuario_id}", response_model=UsuarioRead)
def get_usuario(usuario_id: int, db: Session = Depends(get_db)):
    try:
        return obtener_usuario(usuario_id, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/usuarios/{usuario_id}", response_model=UsuarioRead)
def update_usuario_endpoint(usuario_id: int, usuario: UsuarioUpdate, db: Session = Depends(get_db)):
    try:
        return update_usuario(usuario_id, usuario, db) 
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)      
        )