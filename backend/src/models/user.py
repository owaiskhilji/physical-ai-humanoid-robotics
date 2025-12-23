from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from src.core.database import Base
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import uuid4
import datetime


class UserDB(Base):
    """
    Database model for users (for future authentication)
    """
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(..., max_length=100)
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: str
    is_active: bool
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str