from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority_level: Optional[str] = None
    status: str
    assigned_to: Optional[int] = None
    manager_id: Optional[int] = None
    due_date: Optional[datetime] = None
    related_vendor: Optional[int] = None
    completion_notes: Optional[str] = None
    completion_date: Optional[datetime] = None
    project_id: Optional[int] = None
    event_id: Optional[int] = None
    tenant_id: Optional[int] = None
    event_phase: Optional[str] = None
    recurrence_rule: Optional[str] = None
    recurrence_end_date: Optional[datetime] = None
    parent_task_id: Optional[int] = None
    is_main_task: Optional[bool] = False
    user_group_id: Optional[int] = None
    space_id: Optional[int] = None
    asset_id: Optional[int] = None
    is_archived: Optional[bool] = False
    archived_at: Optional[datetime] = None


class TaskCreate(TaskBase):
    created_by: Optional[int]

    @validator("due_date", "completion_date", "recurrence_end_date", "archived_at", pre=True, always=True)
    def strip_timezone(cls, v):
        if isinstance(v, datetime) and v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority_level: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[int] = None
    manager_id: Optional[int] = None
    due_date: Optional[datetime] = None
    related_vendor: Optional[int] = None
    completion_notes: Optional[str] = None
    completion_date: Optional[datetime] = None
    project_id: Optional[int] = None
    event_id: Optional[int] = None
    tenant_id: Optional[int] = None
    event_phase: Optional[str] = None
    recurrence_rule: Optional[str] = None
    recurrence_end_date: Optional[datetime] = None
    user_group_id: Optional[int] = None
    space_id: Optional[int] = None
    asset_id: Optional[int] = None
    is_archived: Optional[bool] = None
    archived_at: Optional[datetime] = None
    updated_by: Optional[int] = None

    @validator(
        "due_date", "completion_date", "recurrence_end_date", "archived_at",
        pre=True, always=True
    )
    def parse_datetime(cls, v):
        if v in ("", None):
            return None
        if isinstance(v, datetime):
            return v.replace(tzinfo=None)
        return v


class TaskOut(TaskBase):
    task_id: int
    code: Optional[str]
    created_by: Optional[int]
    updated_by: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    assigned_user: Optional[str] = None
    manager_user: Optional[str] = None

    # 🔷 new optional fields
    vendor_name: Optional[str] = None
    project_name: Optional[str] = None
    event_title: Optional[str] = None
    space_label: Optional[str] = None
    asset_name: Optional[str] = None
    parent_task_title: Optional[str] = None
    user_group_name: Optional[str] = None

    class Config:
        orm_mode = True
