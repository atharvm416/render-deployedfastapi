from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# 🔹 Shared base schema for create/update
class UserGroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    tenant_id: int
    member_ids: List[int] = []
    status: str = Field(default='active', pattern='^(active|inactive|archived)$')

class UserGroupCreate(UserGroupBase):
    created_by: Optional[int] = None

class UserGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tenant_id: Optional[int] = None
    member_ids: Optional[List[int]] = None
    status: Optional[str] = Field(default=None, pattern='^(active|inactive|archived)$')
    updated_by: Optional[int] = None

# 🔹 Used in output only
class GroupMember(BaseModel):
    user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None

# 🔹 Final output schema
class UserGroup(BaseModel):
    user_group_id: int
    name: str
    description: Optional[str]
    tenant_id: int
    status: str
    created_by: Optional[int]
    updated_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    members: List[GroupMember] = []  # ✅ Correct: default should be empty list

    code: Optional[str] = None  # 👈 Optional, move to end if not essential

class UserGroupOut(BaseModel):
    user_group_id: int
    name: str
    code: Optional[str]
    description: Optional[str]
    tenant_id: int
    status: str
    created_by: Optional[int]
    updated_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    created_user: Optional[str] = None
    updated_user: Optional[str] = None
    members: List[GroupMember] = []

    class Config:
        orm_mode = True
