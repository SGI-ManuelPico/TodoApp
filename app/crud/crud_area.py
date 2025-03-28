from app.schemas.area import AreaBase, AreaCreate, AreaUpdate, AreaRead
from app.models.models import Area
from sqlalchemy.orm import Session

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



