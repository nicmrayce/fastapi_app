from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=100)
    is_admin: bool = False

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_admin: bool

class Item(BaseModel):
    id: int
    owner_id: int
    name: str
    description: Optional[str] = None
