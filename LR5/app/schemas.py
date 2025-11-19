"""Pydantic-схемы для CRUD операций с пользователями"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, field_validator


def _validate_email(value: Optional[str]) -> Optional[str]:
    if value is None:
        return value
    if "@" not in value:
        raise ValueError("Invalid email address")
    return value


class UserCreate(BaseModel):
    username: str
    email: str
    description: Optional[str] = ""

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        validated = _validate_email(value)
        assert validated is not None
        return validated


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: Optional[str]) -> Optional[str]:
        return _validate_email(value)


class UserRead(BaseModel):
    id: UUID
    username: str
    email: str
    description: Optional[str] = ""
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    name: str
    price: float
    stock_quantity: Optional[int] = 0


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None


class ProductRead(BaseModel):
    id: UUID
    name: str
    price: float
    stock_quantity: int
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: int


class OrderCreate(BaseModel):
    user_id: UUID
    address_id: Optional[UUID] = None
    status: Optional[str] = "pending"
    items: List[OrderItemCreate]


class OrderRead(BaseModel):
    id: UUID
    user_id: UUID
    address_id: Optional[UUID]
    status: str
    total_amount: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
