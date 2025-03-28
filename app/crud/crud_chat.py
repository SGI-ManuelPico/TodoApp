from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.models import Chat, Usuario
from app.schemas.chat import ChatCreate

def create_chat_message(db: Session, chat: ChatCreate, sender_id: int):
    # Verify sender and receiver are in the same area
    sender = db.query(Usuario).filter(Usuario.id == sender_id).first()
    receiver = db.query(Usuario).filter(Usuario.id == chat.receiver_id).first()

    if not sender or not receiver:
        raise ValueError("Sender or receiver not found")

    if sender.area_id != receiver.area_id:
        raise ValueError("Users must be in the same area to chat")

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
    # Verify users are in the same area
    user1 = db.query(Usuario).filter(Usuario.id == user1_id).first()
    user2 = db.query(Usuario).filter(Usuario.id == user2_id).first()

    if not user1 or not user2:
        raise ValueError("One or both users not found")

    if user1.area_id != user2.area_id:
        return []

    messages = db.query(Chat).filter(
        or_(
            and_(Chat.sender_id == user1_id, Chat.receiver_id == user2_id),
            and_(Chat.sender_id == user2_id, Chat.receiver_id == user1_id)
        )
    ).order_by(Chat.timestamp.asc()).all()
    return messages
