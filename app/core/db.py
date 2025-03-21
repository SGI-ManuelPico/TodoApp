from dataclasses import dataclass, field
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

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
        # Build the connection URL
        connection_url = (
            f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}/{self.database}"
        )

        # Create the engine
        self.engine = create_engine(connection_url, echo=self.echo)

        # Configure the sessionmaker
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def get_session(self) -> Session:
        """
        Create and return a new SQLAlchemy session.
        """
        return self.SessionLocal()

db_config = Database(
    host="localhost",
    user="root",
    password="12345678",
    database="inventory",
    echo=True
)

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a DB session for each request,
    and closes it when the request is done.
    """
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()