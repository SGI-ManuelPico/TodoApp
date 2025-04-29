from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.routes import routes_usuario, routes_area, routes_chat, routes_todo
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.core.limiter import limiter
import asyncio
from datetime import datetime, timezone
from sqlalchemy import delete
from app.core.db import get_database
from app.models.models import BlacklistedToken

async def cleanup_expired_tokens():
    """Periodically clean up expired tokens from the blacklist"""
    while True:
        try:
            db = await get_database().get_session()
            now = datetime.now(timezone.utc)
            await db.execute(
                delete(BlacklistedToken).where(BlacklistedToken.expires_at < now)
            )
            await db.commit()
        except Exception as e:
            print(f"Error cleaning up expired tokens: {e}")
        finally:
            if db:
                await db.close()
        await asyncio.sleep(3600)  # Run every hour

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    cleanup_task = asyncio.create_task(cleanup_expired_tokens())
    yield
    # Shutdown
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    if hasattr(app.state, "db"):
        await app.state.db.engine.dispose()

app = FastAPI(lifespan=lifespan)

# Add Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configuración de CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5500",
    "https://todoapp-nmug.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_usuario.router)
app.include_router(routes_area.router)
app.include_router(routes_chat.router)
app.include_router(routes_todo.router)
