from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.models import Area, Usuario
from app.schemas.area import AreaCreate, AreaRead, AreaUpdate
from app.core.security import obtener_usuario_actual
from app.crud.crud_area import *

router = APIRouter()

@router.post("/areas/", response_model=AreaRead)
def crear_area_endpoint(
    area: AreaCreate, 
    db: Session = Depends(get_db),
    _: Usuario = Depends(obtener_usuario_actual) 
):
    try:
        return crear_area(area, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

