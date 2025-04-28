from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.routes import routes_usuario, routes_area, routes_chat, routes_todo

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    if hasattr(app.state, "db"):
        await app.state.db.engine.dispose()

app = FastAPI(lifespan=lifespan)

# Add Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

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
