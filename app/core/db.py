from dataclasses import dataclass, field
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from functools import lru_cache

@dataclass
class Database:
    host: str
    user: str
    password: str
    database: str
    echo: bool = False
    engine: Engine = field(init=False)
    SessionLocal: sessionmaker = field(init=False)

    def __post_init__(self):
        try:
            connection_url = (
                f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}/{self.database}"
            )
            self.engine = create_engine(connection_url, echo=self.echo, pool_pre_ping=True)
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
        except Exception as e:
            raise Exception(f"Database connection failed: {str(e)}")

    def get_session(self) -> Session:
        """
        Create and return a new SQLAlchemy session.
        """
        return self.SessionLocal()

@lru_cache
def get_database() -> Database:
    return Database(
        host="localhost",
        user="root",
        password="12345678",
        database="todoapp",
        echo=True
    )

def get_db() -> Generator[Session, None, None]:
    db = get_database().get_session()
    try:
        yield db
    finally:
        db.close()