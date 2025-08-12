from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class AssetBase(BaseModel):
    name: str
    code: Optional[str] = None
    category: Optional[str] = None
    serial_number: Optional[str] = None
    space_id: Optional[int] = None
    tenant_id: Optional[int] = None
    status: str  # available, in_use, maintenance, retired

    @validator("category", "serial_number", "status", pre=True)
    def empty_string_to_none(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


class AssetCreate(AssetBase):
    created_by: int


class AssetUpdate(AssetBase):
    updated_by: int


class AssetOut(AssetBase):
    asset_id: int
    created_by: Optional[int]
    updated_by: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    space_label: Optional[str] = None

    class Config:
        orm_mode = True
