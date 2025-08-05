from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SpaceBase(BaseModel):
    label: str
    type: str
    capacity: Optional[int] = 0
    status: Optional[str] = "active"
    tenant_id: int

class SpaceCreate(SpaceBase):
    created_by: int

class SpaceUpdate(BaseModel):
    label: Optional[str]
    type: Optional[str]
    capacity: Optional[int]
    status: Optional[str]
    updated_by: int

class Space(SpaceBase):
    space_id: int
    code: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]
    updated_by: Optional[int]

    class Config:
        orm_mode = True
