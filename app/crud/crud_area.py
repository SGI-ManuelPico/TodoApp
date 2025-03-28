from app.schemas.area import AreaBase, AreaCreate, AreaUpdate, AreaRead
from app.models.models import Area
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

def crear_area(area: AreaCreate, db: Session) -> Area:
    try:
        area_data = area.model_dump()
        db_area = Area(**area_data)
        db.add(db_area)
        db.commit()
        db.refresh(db_area)
        return db_area
    except Exception as e:
        db.rollback()
        raise ValueError(f"Error creando area: {str(e)}")

def obtener_area(area_id: int, db: Session):
    return db.query(Area).filter(Area.id == area_id).first()

def actualizar_area(area: Area, area_update: AreaUpdate, db: Session):
    try:
        area_data = area_update.model_dump(exclude_unset=True)
        for key, value in area_data.items():
            setattr(area, key, value)
        db.add(area)
        db.commit()
        db.refresh(area)
        return area
    except Exception as e:
        db.rollback()
        raise ValueError(f"Error updating area: {str(e)}")
