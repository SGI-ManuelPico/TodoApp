from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import routes_usuario, routes_area, routes_chat, routes_todo

app = FastAPI()

# Configuración de CORS
origins = [
    "http://localhost",
    "http://localhost:3000", # Puerto común para React
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Orígenes permitidos
    allow_credentials=True, # Permitir cookies
    allow_methods=["*"],    # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],    # Permitir todas las cabeceras
)

app.include_router(routes_usuario.router)
app.include_router(routes_area.router)
app.include_router(routes_chat.router)
app.include_router(routes_todo.router)
