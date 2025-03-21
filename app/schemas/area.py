from pydantic import BaseModel, Field
from typing import List, Optional

class AreaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    descripcion: str = Field(..., min_length=1, max_length=50)

class AreaCreate(AreaBase):
    pass

class AreaRead(AreaBase):
    id: int

    class Config:
        from_attributes = True

class AreaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    descripcion: Optional[str] = Field(None, min_length=1, max_length=50)

