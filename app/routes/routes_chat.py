from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
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
def send_message(
    chat: ChatCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual)
):
    """
    Send a chat message to another user.
    Users must be in the same area to chat.
    """
    try:
        return crud_chat.create_chat_message(db=db, chat=chat, sender_id=current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Catch unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while sending the message."
        )


@router.get("/{other_user_id}", response_model=List[ChatRead])
def read_messages(
    other_user_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual)
):
    """
    Retrieve chat messages between the current user and another user.
    """
    try:
        # The crud function already checks if users are in the same area
        messages = crud_chat.get_chat_messages(db=db, user1_id=current_user.id, user2_id=other_user_id)
        return messages
    except ValueError as e: # Catch specific errors from CRUD if needed (e.g., user not found)
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, # Or 400 depending on the error
            detail=str(e)
        )
    except Exception as e:
        # Catch unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving messages."
        )
