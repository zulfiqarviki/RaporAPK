from typing import Literal

from pydantic import BaseModel, ConfigDict


UserRole = Literal["admin", "teacher"]


class UserBase(BaseModel):
    nip: str
    name: str


class UserCreate(UserBase):
    password: str
    role: UserRole = "teacher"


class UserUpdate(BaseModel):
    nip: str | None = None
    name: str | None = None
    password: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class UserOut(UserBase):
    id: int
    role: UserRole
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"