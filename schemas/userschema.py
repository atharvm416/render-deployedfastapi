from pydantic import BaseModel, EmailStr, model_validator, StringConstraints
from typing import Optional, List, Annotated
from datetime import datetime

# Base model to inherit from

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    code: Optional[str]
    role: str
    tenant_id: Optional[int]
    first_name: str
    last_name: str
    is_active: Optional[bool] = True
    permissions: Optional[List[str]] = []

    @model_validator(mode='before')
    def at_least_one_contact(cls, values):
        email = values.get('email')
        phone = values.get('phone')
        if not email and not phone:
            raise ValueError("Either 'email' or 'phone' must be provided.")
        return values

class UserCreate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str
    role: str
    tenant_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = True
    permissions: Optional[List[str]] = []
    created_by: Optional[int] = None

    @model_validator(mode='before')
    def at_least_one_contact(cls, values):
        email = values.get('email')
        phone = values.get('phone')
        if not email and not phone:
            raise ValueError("Either 'email' or 'phone' must be provided.")
        return values


class SignInRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=3)]] = None
    password: str

    @model_validator(mode='after')
    def check_email_or_phone(self):
        if not self.email and not self.phone:
            raise ValueError("Either email or phone must be provided.")
        return self

class PasswordUpdateRequest(BaseModel):
    new_password: str

# Input for updating a user
class UserUpdate(BaseModel):
    email: Optional[EmailStr]
    phone: Optional[str]             
    role: Optional[str]
    tenant_id: Optional[int]
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: Optional[bool]
    permissions: Optional[List[str]]
    updated_by: Optional[int]

# Output/response model
class User(BaseModel):
    user_id: int
    code: Optional[str]
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: str
    tenant_id: Optional[int]
    first_name: str
    last_name: str
    is_active: bool
    permissions: Optional[List[str]] = []
    created_by: Optional[int]
    updated_by: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
