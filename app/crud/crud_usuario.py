from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.core.security import hash_password
from app.models.models import Usuario, Area
from sqlalchemy.orm import Session


def crear_usuario(usuario: UsuarioCreate, db: Session) -> Usuario:
    # Verificar si el email ya está registrado
    if db.query(Usuario).filter(Usuario.email == usuario.email).first():
        raise ValueError("Email already registered")
        
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
        raise ValueError(f"Error creating user: {str(e)}")