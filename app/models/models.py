from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuario'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50))
    password = Column(String(50))
    area_id = Column(Integer, ForeignKey('area.id'))

    # Relaciones
    area = relationship('Area', back_populates='usuarios')
    todos = relationship('Todo', back_populates='usuario') 

class Todo(Base):
    __tablename__ = 'todo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    descripcion = Column(String(50))
    prioridad = Column(Integer)
    usuario_id = Column(Integer, ForeignKey('usuario.id'))

    # Relaciones 
    usuario = relationship('Usuario', back_populates='todos')

class Area(Base):
    __tablename__ = 'area'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50))

    # Relaciones
    usuarios = relationship('Usuario', back_populates='area')


