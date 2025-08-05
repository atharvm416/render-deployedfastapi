# models/event.py
from sqlalchemy import Table, Column, Integer, String, Text, ForeignKey, Boolean, DateTime, MetaData

metadata = MetaData()

event = Table(
    "event",
    metadata,
    Column("event_id", Integer, primary_key=True),
    Column("title", Text, nullable=False),
    Column("code", String, unique=True),
    Column("space_id", Integer, ForeignKey("space.space_id", ondelete="SET NULL")),
    Column("tenant_id", Integer, ForeignKey("tenant.tenant_id", ondelete="SET NULL")),
    Column("start_time", DateTime),
    Column("end_time", DateTime),
    Column("status", String),
    Column("is_archived", Boolean, default=False),
    Column("archived_at", DateTime),
    Column("created_by", Integer, ForeignKey("users.user_id", ondelete="SET NULL")),
    Column("updated_by", Integer, ForeignKey("users.user_id", ondelete="SET NULL")),
    Column("created_at", DateTime),
    Column("updated_at", DateTime),
)
