from fastapi import FastAPI
from app.routes import auth as auth_routes
from app.routes import users as users_routes

app = FastAPI(title="Skills Exchange API", version="0.1.0")

app.include_router(auth_routes.router)
app.include_router(users_routes.router)
