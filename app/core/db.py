from dataclasses import dataclass, field
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.engine import Engine
from functools import lru_cache
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass
class Database:
    host: str
    user: str
    password: str
    database: str
    echo: bool = False
    engine: Engine = field(init=False)
    SessionLocal: async_sessionmaker = field(init=False)

    def __post_init__(self):
        try:
            connection_url = (
                f"mysql+aiomysql://{self.user}:{self.password}@{self.host}/{self.database}"
            )
            self.engine = create_async_engine(connection_url, echo=self.echo, pool_pre_ping=True)
            self.SessionLocal = async_sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine,
                class_=AsyncSession
            )
        except Exception as e:
            raise Exception(f"La conexión a la base de datos falló: {str(e)}")

    async def get_session(self) -> AsyncSession:
        """
        Crea una sesión de la base de datos.
        """
        return self.SessionLocal()

##! Falta ver como implementar el pooling de conexiones
@lru_cache
def get_database() -> Database:
    return Database(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'todoapp'),
        echo=os.getenv('DB_ECHO', 'false').lower() == 'true'
    )

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    db = await get_database().get_session()
    try:
        yield db
    finally:
        await db.close()