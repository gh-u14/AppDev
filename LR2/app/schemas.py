"""Pydantic-схемы для CRUD операций с пользователями"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    description: Optional[str] = ""


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    description: Optional[str] = None


class UserRead(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    description: Optional[str] = ""
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
