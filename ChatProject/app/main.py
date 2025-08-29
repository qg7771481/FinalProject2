from fastapi import FastAPI

from app.database import Base, engine
from app.routes import auth, chat, users

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Skills Exchange API")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(chat.router)
