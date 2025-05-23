from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional
from app.utils.validaciones import validar_contraseña
from enum import Enum


class Genero(str, Enum):
    MASCULINO = "Masculino"
    FEMENINO = "Femenino"

class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    genero: Genero
    area_id: int

class UsuarioCreate(BaseModel):
    nombre: str
    email: str
    genero: Genero
    password: str
    area_id: Optional[int] = None

    @field_validator('password')
    def validar_password_create(cls, v):
        return validar_contraseña(v)

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    area_id: Optional[int] = None

    @field_validator('password')
    def validar_password_update(cls, v):
        return validar_contraseña(v)

class UsuarioRead(UsuarioBase):
    id: int

    class Config:
        from_attributes = True

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str | None = None