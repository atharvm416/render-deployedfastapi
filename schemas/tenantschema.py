from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

class TenantBase(BaseModel):
    name: str
    contact_email: Optional[EmailStr] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    @validator("contact_email", "phone", "address", "contact_name", pre=True)
    def empty_string_to_none(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

class TenantCreate(TenantBase):
    pass

class TenantUpdate(TenantBase):
    pass

class Tenant(BaseModel):
    tenant_id: int
    code: Optional[str]
    name: str
    contact_email: Optional[EmailStr] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    user_count: Optional[int] = None
    space_count: Optional[int] = None
    asset_count: Optional[int] = None
    vendor_count: Optional[int] = None
    event_count: Optional[int] = None
    project_count: Optional[int] = None
    task_count: Optional[int] = None


    class Config:
        orm_mode = True
