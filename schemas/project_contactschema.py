from typing import Optional
from pydantic import BaseModel, EmailStr

class ProjectContactBase(BaseModel):
    project_id: int
    contact_type: Optional[str]
    contact_name: Optional[str] = None   # ✅ now optional
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None


class ProjectContactCreate(ProjectContactBase):
    pass

class ProjectContactUpdate(BaseModel):
    contact_type: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


class ProjectContactOut(ProjectContactBase):
    contact_id: int

    class Config:
        orm_mode = True
