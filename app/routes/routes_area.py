from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.models import Area, Usuario
from app.schemas.area import AreaCreate, AreaRead, AreaUpdate
from app.core.security import obtener_usuario_actual
from app.crud.crud_area import *

router = APIRouter(
    prefix='areas',
    tags=['areas']
    )

@router.post("/", response_model=AreaRead)
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


@router.put("/{area_id}", response_model=AreaRead)
def actualizar_area_endpoint(
    area_id: int,
    area_update: AreaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(obtener_usuario_actual)
):
    area = obtener_area(area_id, db)
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Area no encontrada"
        )
    try:
        return actualizar_area(area, area_update, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=list[AreaRead])
def obtener_areas_endpoint(
    db: Session = Depends(get_db),
    _: Usuario = Depends(obtener_usuario_actual)
):
    areas = db.query(Area).all()
    return areas