from fastapi import FastAPI
from app.routes import routes_usuario, routes_area, routes_chat

app = FastAPI()

app.include_router(routes_usuario.router)
app.include_router(routes_area.router)
app.include_router(routes_chat.router)
