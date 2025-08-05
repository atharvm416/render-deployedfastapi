# models/project.py
from sqlalchemy import Table, Column, Integer, String, Text, Date, Boolean, Numeric, ForeignKey, TIMESTAMP, MetaData

metadata = MetaData()

project = Table(
    "project",
    metadata,
    Column("project_id", Integer, primary_key=True),
    Column("name", Text, nullable=False),
    Column("description", Text),
    Column("code", String, unique=True),
    Column("project_type", String, nullable=False),
    Column("status", String),
    Column("owner", Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=False),
    Column("tenant_id", Integer, ForeignKey("tenant.tenant_id", ondelete="SET NULL")),
    Column("start_date", Date, nullable=False),
    Column("end_date", Date),
    Column("priority", String),
    Column("budget", Numeric),
    Column("is_archived", Boolean, default=False),
    Column("archived_at", TIMESTAMP),
    Column("created_by", Integer, ForeignKey("users.user_id", ondelete="SET NULL")),
    Column("updated_by", Integer, ForeignKey("users.user_id", ondelete="SET NULL")),
    Column("created_at", TIMESTAMP),
    Column("updated_at", TIMESTAMP),
)
