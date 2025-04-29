from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Index
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuario'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(50), unique=True, index=True)
    nombre = Column(String(50))
    genero = Column(String(10))
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
    estado = Column(Integer, default=0) # 0: Incompleto, 1: Completo
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

class Chat(Base):
    __tablename__ = 'chat'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey('usuario.id'), nullable=False)
    receiver_id = Column(Integer, ForeignKey('usuario.id'), nullable=False)
    message = Column(String(500), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    sender = relationship('Usuario', foreign_keys=[sender_id])
    receiver = relationship('Usuario', foreign_keys=[receiver_id])

    def __repr__(self):
        return f"Chat(id={self.id}, from={self.sender_id}, to={self.receiver_id})"

class BlacklistedToken(Base):
    __tablename__ = 'blacklisted_tokens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(500), nullable=False)
    blacklisted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return f"BlacklistedToken(id={self.id}, blacklisted_at='{self.blacklisted_at}')"

    # Create an index on token for faster lookups
    __table_args__ = (Index('idx_token', 'token'),)
