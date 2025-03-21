from pydantic import BaseModel
from typing import List, Optional

class Area(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None

class AreaCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class AreaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

class AreaDelete(BaseModel):
    id: int

class AreaList(BaseModel):
    areas: List[Area]