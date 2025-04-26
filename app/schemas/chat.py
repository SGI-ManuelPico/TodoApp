from pydantic import BaseModel
from datetime import datetime

class ChatBase(BaseModel):
    message: str

class ChatCreate(ChatBase):
    receiver_id: int

class ChatUpdate(ChatBase):
    pass

class ChatRead(ChatBase):
    id: int
    sender_id: int
    receiver_id: int
    timestamp: datetime

    class Config:
        from_attributes = True
