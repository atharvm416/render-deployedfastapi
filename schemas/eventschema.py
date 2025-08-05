from datetime import datetime
from pydantic import BaseModel, validator
from typing import Optional, List
import dateutil.parser
from schemas.eventcontactschema import EventContactOut

class EventBase(BaseModel):
    title: str
    space_id: Optional[int] = None
    tenant_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None
    is_archived: Optional[bool] = False

    @validator("start_time", "end_time", pre=True)
    def strip_timezone(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            dt = dateutil.parser.parse(v)
        elif isinstance(v, datetime):
            dt = v
        else:
            raise ValueError("Invalid datetime value")

        # remove tzinfo if present
        if dt.tzinfo:
            return dt.replace(tzinfo=None)
        return dt


class EventCreate(EventBase):
    created_by: Optional[int]

class EventUpdate(BaseModel):
    title: Optional[str] = None
    space_id: Optional[int] = None
    tenant_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None
    is_archived: Optional[bool] = None
    updated_by: Optional[int]

    @validator("start_time", "end_time", pre=True)
    def strip_timezone(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            dt = dateutil.parser.parse(v)
        elif isinstance(v, datetime):
            dt = v
        else:
            raise ValueError("Invalid datetime value")
        if dt.tzinfo:
            return dt.replace(tzinfo=None)
        return dt

class EventOut(EventBase):
    event_id: int
    code: Optional[str]
    created_by: Optional[int]
    updated_by: Optional[int]
    archived_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    created_user: Optional[str] = None
    updated_user: Optional[str] = None
    space_label: Optional[str] = None

class EventOutWithContacts(EventOut):
    event_id: int
    code: Optional[str]
    created_by: Optional[int]
    updated_by: Optional[int]
    archived_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    contacts: List[EventContactOut] = []

    class Config:
        orm_mode = True
