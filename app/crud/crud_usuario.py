from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.core.security import hash_password
from app.models.models import Usuario, Area
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def crear_usuario(usuario: UsuarioCreate, db: AsyncSession) -> Usuario:
    # Verificar si el email ya está registrado
    """
    Crea un nuevo usuario.
    
    Verifica si el email ya está registrado. Si lo está, lanza un ValueError.
    
    Args:
        usuario (UsuarioCreate): Información del usuario a crear.
        db (AsyncSession): Sesión asincrónica de la base de datos.
    
    Returns:
        Usuario: El usuario creado.
    
    Raises:
        ValueError: Si el email ya está registrado, o si ocurre un error durante la creación del usuario.
    """

    result = await db.execute(select(Usuario).filter(Usuario.email == usuario.email))
    if result.scalar_one_or_none():
        raise ValueError("Este email ya está registrado")
        
    try:
        usuario_data = usuario.model_dump()
        usuario_data["password"] = hash_password(usuario_data["password"])
        db_usuario = Usuario(**usuario_data)
        db.add(db_usuario)
        await db.commit()
        await db.refresh(db_usuario)
        return db_usuario
    except Exception as e:
        await db.rollback()
        raise ValueError(f"Error creando el usuario: {str(e)}")

async def obtener_usuario(usuario_id: int, db: AsyncSession) -> Usuario:
    """
    Obtiene un usuario específico por su ID.

    Args:
        usuario_id (int): ID del usuario a obtener.
        db (AsyncSession): Sesión asincrónica de la base de datos.

    Returns:
        Usuario: Instancia del usuario obtenido.

    Raises:
        ValueError: Si el usuario no se encuentra en la base de datos.
    """

    result = await db.execute(select(Usuario).filter(Usuario.id == usuario_id))
    usuario = result.scalar_one_or_none()
    if usuario is None:
        raise ValueError(f"Usuario con id {usuario_id} no encontrado")
    return usuario

async def update_usuario(usuario_id: int, usuario: UsuarioUpdate, db: AsyncSession) -> Usuario:
    """
    Actualiza un usuario específico por su ID.

    Args:
        usuario_id (int): ID del usuario a actualizar.
        usuario (UsuarioUpdate): Esquema con los datos actualizados del usuario.
        db (AsyncSession): Sesión asincrónica de la base de datos.

    Returns:
        Usuario: Instancia del usuario actualizado.

    Raises:
        ValueError: Si el usuario no se encuentra en la base de datos o si ocurre un error al actualizar.
    """

    db_usuario = await obtener_usuario(usuario_id, db)
    
    update_data = usuario.model_dump(exclude_unset=True)

    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])
    
    for field, value in update_data.items():
        setattr(db_usuario, field, value)
        
    try:
        await db.commit()
        await db.refresh(db_usuario)
        return db_usuario
    except Exception as e:
        await db.rollback()
        raise ValueError(f"Error updating user: {str(e)}")