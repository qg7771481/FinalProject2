from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.skill import Skill, user_skills
from app.models.chat import Message


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    skills = relationship("Skill", secondary=user_skills, back_populates="users")

    messages_sent = relationship(
        "Message",
        back_populates="sender",
        foreign_keys=[Message.sender_id]
    )


    messages_received = relationship(
        "Message",
        back_populates="receiver",
        foreign_keys=[Message.receiver_id]
    )