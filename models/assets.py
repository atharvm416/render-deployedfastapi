from sqlalchemy import (
    Table, Column, Integer, String, Text, ForeignKey, TIMESTAMP,
    CheckConstraint, MetaData
)
from sqlalchemy.sql import func

metadata = MetaData()

asset = Table(
    "asset", metadata,
    Column("asset_id", Integer, primary_key=True),
    Column("name", Text, nullable=False),
    Column("code", Text, unique=True),
    Column("category", Text),
    Column("serial_number", Text),
    Column("space_id", Integer, ForeignKey("space.space_id", ondelete="SET NULL")),
    Column("tenant_id", Integer, ForeignKey("tenant.tenant_id", ondelete="SET NULL")),
    Column("status", Text, CheckConstraint(
        "status IN ('available', 'in_use', 'maintenance', 'retired')"
    )),
    Column("created_by", Integer, ForeignKey("users.user_id", ondelete="SET NULL")),
    Column("updated_by", Integer, ForeignKey("users.user_id", ondelete="SET NULL")),
    Column("created_at", TIMESTAMP, server_default=func.now()),
    Column("updated_at", TIMESTAMP, server_default=func.now(), onupdate=func.now())
)
