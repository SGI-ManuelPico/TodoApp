from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuario'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(50), unique=True, index=True)
    nombre = Column(String(50))
    password = Column(String(100))
    area_id = Column(Integer, ForeignKey('area.id'))

    # Relaciones
    area = relationship('Area', back_populates='usuarios')
    todos = relationship('Todo', back_populates='usuario', cascade="all, delete-orphan") 
    
    def __repr__(self):
        return f"Usuario(id={self.id}, nombre='{self.nombre}')"

class Todo(Base):
    __tablename__ = 'todo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    descripcion = Column(String(50))
    prioridad = Column(Integer)
    usuario_id = Column(Integer, ForeignKey('usuario.id'))

    # Relaciones 
    usuario = relationship('Usuario', back_populates='todos')
    
    def __repr__(self):
        return f"Todo(id={self.id}, descripcion='{self.descripcion}', prioridad={self.prioridad})"

class Area(Base):
    __tablename__ = 'area'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50))
    descripcion = Column(String(50))
    
    def __repr__(self):
        return f"Area(id={self.id}, nombre='{self.nombre}, descripcion='{self.descripcion}')"

    # Relaciones
    usuarios = relationship('Usuario', back_populates='area')