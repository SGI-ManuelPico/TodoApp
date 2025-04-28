from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Todo, Usuario
from app.schemas.todo import TodoCreate, TodoUpdate

async def crear_todo(db: AsyncSession, todo: TodoCreate, usuario_id: int):
    """Crea un nuevo Todo asociado a un usuario."""
    db_todo = Todo(**todo.model_dump(), usuario_id=usuario_id)
    db.add(db_todo)
    await db.commit()
    await db.refresh(db_todo)
    return db_todo

async def obtener_todo(db: AsyncSession, todo_id: int, usuario_id: int):
    """Obtiene un Todo específico por ID, asegurándose de que pertenezca al usuario."""
    result = await db.execute(
        select(Todo).filter(Todo.id == todo_id, Todo.usuario_id == usuario_id)
    )
    return result.scalar_one_or_none()

async def obtener_todos(db: AsyncSession, usuario_id: int, skip: int = 0, limit: int = 100):
    """Obtiene todos los Todos de un usuario específico."""
    result = await db.execute(
        select(Todo)
        .filter(Todo.usuario_id == usuario_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def actualizar_todo(db: AsyncSession, todo_id: int, todo_update: TodoUpdate, usuario_id: int):
    """Actualiza un Todo específico, asegurándose de que pertenezca al usuario."""
    result = await db.execute(
        select(Todo).filter(Todo.id == todo_id, Todo.usuario_id == usuario_id)
    )
    db_todo = result.scalar_one_or_none()
    if db_todo is None:
        return None

    update_data = todo_update.model_dump(exclude_unset=True)
    for var, value in update_data.items():
        if value is not None:
            setattr(db_todo, var, value)
    
    await db.commit()
    await db.refresh(db_todo)
    return db_todo

async def eliminar_todo(db: AsyncSession, todo_id: int, usuario_id: int):
    """Elimina un Todo específico, asegurándose de que pertenezca al usuario."""
    result = await db.execute(
        select(Todo).filter(Todo.id == todo_id, Todo.usuario_id == usuario_id)
    )
    db_todo = result.scalar_one_or_none()
    if db_todo is None:
        return None
    
    await db.delete(db_todo)
    await db.commit()
    return db_todo

async def obtener_todos_por_prioridad_igual(db: AsyncSession, usuario_id: int, prioridad: int, skip: int = 0, limit: int = 100):
    """Obtiene todos los Todos de un usuario con una prioridad específica."""
    result = await db.execute(
        select(Todo)
        .filter(Todo.usuario_id == usuario_id, Todo.prioridad == prioridad)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def obtener_todos_por_prioridad_mayor_igual(db: AsyncSession, usuario_id: int, prioridad: int, skip: int = 0, limit: int = 100):
    """Obtiene todos los Todos de un usuario con prioridad mayor o igual a la especificada."""
    result = await db.execute(
        select(Todo)
        .filter(Todo.usuario_id == usuario_id, Todo.prioridad >= prioridad)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def obtener_todos_por_prioridad_menor_igual(db: AsyncSession, usuario_id: int, prioridad: int, skip: int = 0, limit: int = 100):
    """Obtiene todos los Todos de un usuario con prioridad menor o igual a la especificada."""
    result = await db.execute(
        select(Todo)
        .filter(Todo.usuario_id == usuario_id, Todo.prioridad <= prioridad)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def eliminar_todos_completados(db: AsyncSession, usuario_id: int):
    """Elimina todos los Todos completados (estado=1) de un usuario específico."""
    result = await db.execute(
        select(Todo).filter(Todo.usuario_id == usuario_id, Todo.estado == 1)
    )
    todos_completados = result.scalars().all()
    for todo in todos_completados:
        await db.delete(todo)
    
    await db.commit()
    return len(todos_completados)
