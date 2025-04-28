from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from app.models.models import Chat, Usuario
from app.schemas.chat import ChatCreate

async def create_chat_message(db: AsyncSession, chat: ChatCreate, sender_id: int):
    # Verifica que el remitente y el receptor estén en la misma área
    """
    Crea un nuevo mensaje en el chat entre dos usuarios.

    Args:
        db (AsyncSession): Sesión de la base de datos.
        chat (ChatCreate): Esquema con los datos del mensaje a crear.
        sender_id (int): ID del remitente del mensaje.

    Returns:
        Chat: Esquema con los datos del mensaje creado.

    Raises:
        ValueError: Si el remitente o el receptor no existen, o si los usuarios
            no están en la misma área.
    """
    result = await db.execute(
        select(Usuario).filter(Usuario.id.in_([sender_id, chat.receiver_id]))
    )
    users = result.scalars().all()
    if len(users) != 2:
        raise ValueError("Remitente o receptor no encontrado")

    sender, receiver = users[0], users[1]
    if sender.area_id != receiver.area_id:
        raise ValueError("Los usuarios deben estar en la misma área para chatear")

    db_chat = Chat(
        sender_id=sender_id,
        receiver_id=chat.receiver_id,
        message=chat.message
    )
    
    db.add(db_chat)
    await db.commit()
    await db.refresh(db_chat)
    return db_chat

async def get_chat_messages(db: AsyncSession, user1_id: int, user2_id: int):
    # Verifica que ambos usuarios existan y estén en la misma área
    """
    Obtiene los mensajes del chat entre dos usuarios.

    Args:
        db (AsyncSession): Sesión de la base de datos.
        user1_id (int): ID del primer usuario.
        user2_id (int): ID del segundo usuario.

    Returns:
        List[Chat]: Lista de mensajes entre los dos usuarios, ordenados por
        fecha de envío ascendente. Retorna una lista vacía si los usuarios no
        están en la misma área o si no se encuentran.

    Raises:
        ValueError: Si uno o ambos usuarios no existen.
    """

    result = await db.execute(
        select(Usuario).filter(Usuario.id.in_([user1_id, user2_id]))
    )
    users = result.scalars().all()
    if len(users) != 2:
        raise ValueError("Uno o ambos usuarios no encontrados")

    if users[0].area_id != users[1].area_id:
        return []

    result = await db.execute(
        select(Chat).filter(
            or_(
                and_(Chat.sender_id == user1_id, Chat.receiver_id == user2_id),
                and_(Chat.sender_id == user2_id, Chat.receiver_id == user1_id)
            )
        ).order_by(Chat.timestamp.asc())
    )
    return result.scalars().all()

async def editar_mensaje(db: AsyncSession, chat_id: int, message: str):
    """
    Edita un mensaje previamente enviado.

    Args:
        db (AsyncSession): Sesión de la base de datos.
        chat_id (int): ID del mensaje a editar.
        message (str): Contenido del mensaje a editar.

    Returns:
        Chat: Esquema con los datos del mensaje editado.

    Raises:
        ValueError: Si el mensaje no existe.
    """
    result = await db.execute(select(Chat).filter(Chat.id == chat_id))
    chat = result.scalar_one_or_none()
    if not chat:
        raise ValueError("Mensaje no encontrado")
    chat.message = message
    await db.commit()
    return chat

async def eliminar_mensaje(db: AsyncSession, chat_id: int):
    """
    Elimina un mensaje previamente enviado.

    Args:
        db (AsyncSession): Sesión de la base de datos.
        chat_id (int): ID del mensaje a eliminar.

    Raises:
        ValueError: Si el mensaje no existe.
    """
    result = await db.execute(select(Chat).filter(Chat.id == chat_id))
    chat = result.scalar_one_or_none()
    if not chat:
        raise ValueError("Mensaje no encontrado")
    await db.delete(chat)
    await db.commit()