from pydantic import BaseModel
from typing import List, Optional

class UsuarioBase(BaseModel):
    nombre: str
    email: str
    password: str
    area_id: int

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioRead(UsuarioBase):
    id: int

    class Config:
        from_attributes = True

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    area_id: Optional[int] = None



