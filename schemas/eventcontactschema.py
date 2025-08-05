# schemas/eventcontactschema.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class EventContactBase(BaseModel):
    event_id: int
    contact_type: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None

class EventContactCreate(EventContactBase):
    pass

class EventContactUpdate(BaseModel):
    contact_type: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None

class EventContactOut(EventContactBase):
    contact_id: int

    class Config:
        orm_mode = True
