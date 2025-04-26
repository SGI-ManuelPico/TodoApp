from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.models import Chat, Usuario
from app.schemas.chat import ChatCreate

def create_chat_message(db: Session, chat: ChatCreate, sender_id: int):
    # Verifica que el remitente y el receptor estén en la misma área
    sender = db.query(Usuario).filter(Usuario.id == sender_id).first()
    receiver = db.query(Usuario).filter(Usuario.id == chat.receiver_id).first()

    if not sender or not receiver:
        raise ValueError("Remitente o receptor no encontrado")

    if sender.area_id != receiver.area_id:
        raise ValueError("Los usuarios deben estar en la misma área para chatear")

    db_chat = Chat(
        sender_id=sender_id,
        receiver_id=chat.receiver_id,
        message=chat.message
    )
    
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

def get_chat_messages(db: Session, user1_id: int, user2_id: int):
    # Verifica que ambos usuarios existan y estén en la misma área
    user1 = db.query(Usuario).filter(Usuario.id == user1_id).first()
    user2 = db.query(Usuario).filter(Usuario.id == user2_id).first()

    if not user1 or not user2:
        raise ValueError("Uno o ambos usuarios no encontrados")

    if user1.area_id != user2.area_id:
        return []

    messages = db.query(Chat).filter(
        or_(
            and_(Chat.sender_id == user1_id, Chat.receiver_id == user2_id),
            and_(Chat.sender_id == user2_id, Chat.receiver_id == user1_id)
        )
    ).order_by(Chat.timestamp.asc()).all()
    return messages

def editar_mensaje(db: Session, chat_id: int, message: str):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise ValueError("Mensaje no encontrado")
    chat.message = message
    db.commit()
    return chat

def eliminar_mensaje(db: Session, chat_id: int):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise ValueError("Mensaje no encontrado")
    db.delete(chat)
    db.commit()