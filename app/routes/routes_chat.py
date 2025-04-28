from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.db import get_db
from app.models.models import Usuario
from app.schemas.chat import ChatCreate, ChatRead
from app.core.security import obtener_usuario_actual
from app.crud import crud_chat

router = APIRouter(
    prefix="/chats",
    tags=["chats"],
    dependencies=[Depends(obtener_usuario_actual)]
)

@router.post("/", response_model=ChatRead)
async def enviar_mensaje(
    chat: ChatCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual)
):
    """
    Envía un mensaje entre dos usuarios.
    Los usuarios deben estar en la misma área para enviar mensajes.
    El remitente es el usuario actual.
    """
    try:
        return await crud_chat.create_chat_message(db=db, chat=chat, sender_id=current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error al enviar el mensaje."
        )

@router.get("/{other_user_id}", response_model=List[ChatRead])
async def leer_mensajes(
    other_user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual)
):
    """
    Obtiene los mensajes entre el usuario actual y otro usuario.
    Los usuarios deben estar en la misma área para ver los mensajes.
    """
    try:
        messages = await crud_chat.get_chat_messages(db=db, user1_id=current_user.id, user2_id=other_user_id)
        return messages
    except ValueError as e:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error al obtener los mensajes."
        )

@router.put("/{chat_id}", response_model=ChatRead)
async def editar_mensaje_endpoint(
    chat_id: int,
    message: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual)
):
    """
    Edita un mensaje previamente enviado.
    Sólo el remitente del mensaje puede editar el mensaje.
    """
    try:
        return await crud_chat.editar_mensaje(db=db, chat_id=chat_id, message=message)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error al editar el mensaje."
        )

@router.delete("/{chat_id}", status_code=status.HTTP_200_OK)
async def eliminar_mensaje_endpoint(
    chat_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual)
):
    """
    Elimina un mensaje previamente enviado.
    Sólo el remitente del mensaje puede eliminar el mensaje.
    """
    try:
        await crud_chat.eliminar_mensaje(db=db, chat_id=chat_id)
        return {"detail": "Mensaje eliminado correctamente"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error al eliminar el mensaje."
        )