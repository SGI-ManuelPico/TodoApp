from pydantic import BaseModel, Field
from typing import List, Optional
from enum import IntEnum

class Prioridad(IntEnum):
    BAJA = 1
    MEDIA = 2
    ALTA = 3
    URGENTE = 4
    CRITICA = 5

class TodoBase(BaseModel):
    descripcion: str = Field(..., min_length=1, max_length=50)
    prioridad: Prioridad
    estado: int = Field(0, ge=0, le=1) # 0: Incompleto, 1: Completo

class TodoCreate(TodoBase):
    pass 

class TodoRead(TodoBase):
    id: int
    
    class Config:
        from_attributes = True

class TodoUpdate(BaseModel):
    descripcion: Optional[str] = Field(None, min_length=1, max_length=50)
    prioridad: Optional[Prioridad] = None
    estado: Optional[int] = Field(None, ge=0, le=1)
