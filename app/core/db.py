from dataclasses import dataclass, field
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
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
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'todoapp'),
        echo=os.getenv('DB_ECHO', 'false').lower() == 'true'
    )

def get_db() -> Generator[Session, None, None]:
    db = get_database().get_session()
    try:
        yield db
    finally:
        db.close()
