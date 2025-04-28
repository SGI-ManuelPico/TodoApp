from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.models.models import Area, Usuario
from app.schemas.area import AreaCreate, AreaRead, AreaUpdate
from app.core.security import obtener_usuario_actual
from app.crud.crud_area import *

router = APIRouter(
    prefix='/areas',
    tags=['areas']
)

@router.post("/", response_model=AreaRead)
async def crear_area_endpoint(
    area: AreaCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(obtener_usuario_actual)
):
    """
    Crea una nueva Área.

    Args:
        area (AreaCreate): Esquema con los datos del Area a crear.
        db (AsyncSession): Sesión de la base de datos.
        _ (Usuario): Usuario autenticado.

    Returns:
        AreaRead: Esquema con los datos del Area creado.
    """

    try:
        return await crear_area(area, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{area_id}", response_model=AreaRead)
async def actualizar_area_endpoint(
    area_id: int,
    area_update: AreaUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(obtener_usuario_actual)
):
    """
    Actualiza un Area existente.

    Args:
        area_id (int): ID del Area a actualizar.
        area_update (AreaUpdate): Esquema con los datos actualizados del Area.
        db (AsyncSession): Sesión de la base de datos.
        _ (Usuario): Usuario autenticado.

    Returns:
        AreaRead: Esquema con los datos actualizados del Area.

    Raises:
        HTTPException: Si el Area no existe o si ocurre un error al actualizar.
    """

    area = await obtener_area(area_id, db)
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Area no encontrada"
        )
    try:
        return await actualizar_area(area, area_update, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=list[AreaRead])
async def obtener_areas_endpoint(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(obtener_usuario_actual)
):
    """
    Obtiene todas las áreas existentes en la base de datos.

    Args:
        db (AsyncSession): Sesión de la base de datos.
        _ (Usuario): Usuario autenticado.

    Returns:
        list[AreaRead]: Lista de áreas existentes.
    """
    result = await db.execute(select(Area))
    return result.scalars().all()