from app.schemas.area import AreaBase, AreaCreate, AreaUpdate, AreaRead
from app.models.models import Area, Usuario
from sqlalchemy.orm import Session

def crear_area(area: AreaCreate, db: Session, usuario_creador: Usuario) -> Area:
    try:
        area_data = area.model_dump()
        area_data["id_usuario_creador"] = usuario_creador.id 
        db_area = Area(**area_data)
        db.add(db_area)
        db.commit()
        db.refresh(db_area)
        return db_area
    except Exception as e:
        db.rollback()
        raise ValueError(f"Error creando area: {str(e)}")



