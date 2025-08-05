from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class VendorBase(BaseModel):
    name: str
    description: Optional[str] = None
    vendor_type: str
    status: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile_number: Optional[str] = None
    website: Optional[str] = None
    contact_name: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
    tax_id: Optional[str] = None
    compliance_status: Optional[str] = None
    payment_terms: Optional[str] = None
    discount_rate: Optional[float] = None
    credit_limit: Optional[float] = None
    tenant_id: int


class VendorCreate(VendorBase):
    created_by: int


class VendorUpdate(VendorBase):
    updated_by: int


class VendorOut(VendorBase):
    vendor_id: int
    code: Optional[str]
    created_by: Optional[int]
    updated_by: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
