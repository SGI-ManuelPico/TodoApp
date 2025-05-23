from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.security import obtener_usuario_actual, reintentar_operacion
from app.schemas.todo import TodoCreate, TodoRead, TodoUpdate, Prioridad
from app.schemas.usuario import UsuarioRead
from app.crud import crud_todo
from app.models.models import Usuario

router = APIRouter(
    prefix="/todos", 
    tags=["todos"] 
)

@router.post("/", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
async def crear_todo_endpoint(
    todo: TodoCreate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """Crea un nuevo Todo para el usuario autenticado."""
    return await reintentar_operacion(
        lambda: crud_todo.crear_todo(db=db, todo=todo, usuario_id=usuario_actual.id)
    )

@router.delete("/completados", status_code=status.HTTP_200_OK)
async def eliminar_todos_completados_endpoint(
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """Elimina todos los Todos completados (estado=1) del usuario autenticado."""
    num_eliminados = await reintentar_operacion(
        lambda: crud_todo.eliminar_todos_completados(db=db, usuario_id=usuario_actual.id)
    )
    return {"message": f"{num_eliminados} tareas completadas eliminadas correctamente"}

@router.get("/{todo_id}", response_model=TodoRead)
async def obtener_todo_endpoint(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """Obtiene un Todo específico del usuario autenticado."""
    db_todo = await reintentar_operacion(
        lambda: crud_todo.obtener_todo(db=db, todo_id=todo_id, usuario_id=usuario_actual.id)
    )
    if db_todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo no encontrado")
    return db_todo

@router.get("/", response_model=List[TodoRead])
async def obtener_todos_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """Obtiene todos los Todos del usuario autenticado."""
    todos = await reintentar_operacion(
        lambda: crud_todo.obtener_todos(db=db, usuario_id=usuario_actual.id, skip=skip, limit=limit)
    )
    return todos

@router.put("/{todo_id}", response_model=TodoRead)
async def actualizar_todo_endpoint(
    todo_id: int,
    todo_update: TodoUpdate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """Actualiza un Todo específico del usuario autenticado."""
    db_todo = await reintentar_operacion(
        lambda: crud_todo.actualizar_todo(db=db, todo_id=todo_id, todo_update=todo_update, usuario_id=usuario_actual.id)
    )
    if db_todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo no encontrado")
    return db_todo

@router.delete("/{todo_id}", status_code=status.HTTP_200_OK)
async def eliminar_todo_endpoint(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """Elimina un Todo específico del usuario autenticado."""
    db_todo = await reintentar_operacion(
        lambda: crud_todo.eliminar_todo(db=db, todo_id=todo_id, usuario_id=usuario_actual.id)
    )
    if db_todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo no encontrado")
    return {"message": "Todo eliminado correctamente"}

@router.get("/prioridad/igual/{prioridad}", response_model=List[TodoRead])
async def obtener_todos_por_prioridad_igual_endpoint(
    prioridad: Prioridad,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """Obtiene todos los Todos del usuario con una prioridad específica."""
    todos = await reintentar_operacion(
        lambda: crud_todo.obtener_todos_por_prioridad_igual(
            db=db, usuario_id=usuario_actual.id, prioridad=prioridad.value, skip=skip, limit=limit
        )
    )
    return todos

@router.get("/prioridad/mayor_igual/{prioridad}", response_model=List[TodoRead])
async def obtener_todos_por_prioridad_mayor_igual_endpoint(
    prioridad: Prioridad,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """Obtiene todos los Todos del usuario con prioridad mayor o igual a la especificada."""
    todos = await reintentar_operacion(
        lambda: crud_todo.obtener_todos_por_prioridad_mayor_igual(
            db=db, usuario_id=usuario_actual.id, prioridad=prioridad.value, skip=skip, limit=limit
        )
    )
    return todos

@router.get("/prioridad/menor_igual/{prioridad}", response_model=List[TodoRead])
async def obtener_todos_por_prioridad_menor_igual_endpoint(
    prioridad: Prioridad,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """Obtiene todos los Todos del usuario con prioridad menor o igual a la especificada."""
    todos = await reintentar_operacion(
        lambda: crud_todo.obtener_todos_por_prioridad_menor_igual(
            db=db, usuario_id=usuario_actual.id, prioridad=prioridad.value, skip=skip, limit=limit
        )
    )
    return todos
