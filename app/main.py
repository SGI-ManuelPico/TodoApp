from fastapi import FastAPI
from app.routes import routes_usuario

app = FastAPI()

app.include_router(routes_usuario.router)