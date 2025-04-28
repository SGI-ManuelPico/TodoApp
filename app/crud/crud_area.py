from app.schemas.area import AreaBase, AreaCreate, AreaUpdate, AreaRead
from app.models.models import Area
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def crear_area(area: AreaCreate, db: AsyncSession) -> Area:
    try:
        area_data = area.model_dump()
        db_area = Area(**area_data)
        db.add(db_area)
        await db.commit()
        await db.refresh(db_area)
        return db_area
    except Exception as e:
        await db.rollback()
        raise ValueError(f"Error creando area: {str(e)}")

async def obtener_area(area_id: int, db: AsyncSession):
    result = await db.execute(select(Area).filter(Area.id == area_id))
    return result.scalar_one_or_none()

async def actualizar_area(area: Area, area_update: AreaUpdate, db: AsyncSession):
    try:
        area_data = area_update.model_dump(exclude_unset=True)
        for key, value in area_data.items():
            setattr(area, key, value)
        db.add(area)
        await db.commit()
        await db.refresh(area)
        return area
    except Exception as e:
        await db.rollback()
        raise ValueError(f"Error updating area: {str(e)}")
