from sqlalchemy.orm import Session
from app.models.models import Todo, Usuario
from app.schemas.todo import TodoCreate, TodoUpdate

def crear_todo(db: Session, todo: TodoCreate, usuario_id: int):
    """Crea un nuevo Todo asociado a un usuario."""
    db_todo = Todo(**todo.model_dump(), usuario_id=usuario_id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def obtener_todo(db: Session, todo_id: int, usuario_id: int):
    """Obtiene un Todo específico por ID, asegurándose de que pertenezca al usuario."""
    return db.query(Todo).filter(Todo.id == todo_id, Todo.usuario_id == usuario_id).first()

def obtener_todos(db: Session, usuario_id: int, skip: int = 0, limit: int = 100):
    """Obtiene todos los Todos de un usuario específico."""
    return db.query(Todo).filter(Todo.usuario_id == usuario_id).offset(skip).limit(limit).all()

def actualizar_todo(db: Session, todo_id: int, todo_update: TodoUpdate, usuario_id: int):
    """Actualiza un Todo específico, asegurándose de que pertenezca al usuario."""
    db_todo = db.query(Todo).filter(Todo.id == todo_id, Todo.usuario_id == usuario_id).first()
    if db_todo is None:
        return None

    # Obtener los datos del schema que no son None
    update_data = todo_update.model_dump(exclude_unset=True)

    for var, value in update_data.items():
        if value is not None:
            setattr(db_todo, var, value)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def eliminar_todo(db: Session, todo_id: int, usuario_id: int):
    """Elimina un Todo específico, asegurándose de que pertenezca al usuario."""
    db_todo = db.query(Todo).filter(Todo.id == todo_id, Todo.usuario_id == usuario_id).first()
    if db_todo is None:
        return None
    db.delete(db_todo)
    db.commit()
    return db_todo

# Funciones para filtrar por prioridad
def obtener_todos_por_prioridad_igual(db: Session, usuario_id: int, prioridad: int, skip: int = 0, limit: int = 100):
    """Obtiene todos los Todos de un usuario con una prioridad específica."""
    return db.query(Todo).filter(Todo.usuario_id == usuario_id, Todo.prioridad == prioridad).offset(skip).limit(limit).all()

def obtener_todos_por_prioridad_mayor_igual(db: Session, usuario_id: int, prioridad: int, skip: int = 0, limit: int = 100):
    """Obtiene todos los Todos de un usuario con prioridad mayor o igual a la especificada."""
    return db.query(Todo).filter(Todo.usuario_id == usuario_id, Todo.prioridad >= prioridad).offset(skip).limit(limit).all()

def obtener_todos_por_prioridad_menor_igual(db: Session, usuario_id: int, prioridad: int, skip: int = 0, limit: int = 100):
    """Obtiene todos los Todos de un usuario con prioridad menor o igual a la especificada."""
    return db.query(Todo).filter(Todo.usuario_id == usuario_id, Todo.prioridad <= prioridad).offset(skip).limit(limit).all()

def eliminar_todos_completados(db: Session, usuario_id: int):
    """Elimina todos los Todos completados (estado=1) de un usuario específico."""
    num_eliminados = db.query(Todo).filter(Todo.usuario_id == usuario_id, Todo.estado == 1).delete()
    db.commit()
    return num_eliminados # Retorna el número de filas eliminadas
