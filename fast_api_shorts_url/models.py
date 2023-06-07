from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from datetime import datetime

from database import Base
from routers.auth import get_password_hash


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    shorts = relationship("Shorts", back_populates="owner")


class Shorts(Base):
    __tablename__ = "shorts"

    id = Column(Integer, primary_key=True, index=True)
    origin_url = Column(String, index=True)
    short_url = Column(String, index=True, unique=True,)
    visits = Column(Integer, default=0, index=True)
    date_created = Column(DateTime, default=datetime.now)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("Users", back_populates="shorts")
