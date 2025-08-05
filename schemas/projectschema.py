# schemas/projectschema.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from schemas.project_contactschema import ProjectContactOut

class ProjectBase(BaseModel):
    name: str
    description: Optional[str]
    project_type: str
    status: Optional[str]
    owner: int
    tenant_id: Optional[int]
    start_date: date
    end_date: Optional[date]
    priority: Optional[str]
    budget: Optional[float]
    is_archived: Optional[bool] = False

class ProjectCreate(ProjectBase):
    created_by: int

class ProjectUpdate(ProjectBase):
    updated_by: int

class ProjectOut(ProjectBase):
    project_id: int
    code: Optional[str]
    archived_at: Optional[datetime]
    created_by: Optional[int]
    updated_by: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    created_user: Optional[str] = None  # 👈 added
    updated_user: Optional[str] = None  # 👈 added
    
    contacts: List[ProjectContactOut] = [] 

    class Config:
        orm_mode = True
