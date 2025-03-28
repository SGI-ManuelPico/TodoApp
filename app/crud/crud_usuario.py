from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.core.security import hash_password
from app.models.models import Usuario, Area
from sqlalchemy.orm import Session


def crear_usuario(usuario: UsuarioCreate, db: Session) -> Usuario:
    # Verificar si el email ya está registrado
    if db.query(Usuario).filter(Usuario.email == usuario.email).first():
        raise ValueError("Este email ya está registrado")
        
    try:
        usuario_data = usuario.model_dump()
        usuario_data["password"] = hash_password(usuario_data["password"])
        db_usuario = Usuario(**usuario_data)
        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)
        return db_usuario
    except Exception as e:
        db.rollback()
        raise ValueError(f"Error creando el usuario: {str(e)}")

def obtener_usuario(usuario_id: int, db: Session) -> Usuario:
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise ValueError(f"Usuario con id {usuario_id} no encontrado")
    return usuario

def update_usuario(usuario_id: int, usuario: UsuarioUpdate, db: Session) -> Usuario:
    db_usuario = obtener_usuario(usuario_id, db)
    
    update_data = usuario.model_dump(exclude_unset=True)

    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])
    
    for field, value in update_data.items():
        setattr(db_usuario, field, value)
        
    try:
        db.commit()
        db.refresh(db_usuario)
        return db_usuario
    except Exception as e:
        db.rollback()
        raise ValueError(f"Error updating user: {str(e)}")