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