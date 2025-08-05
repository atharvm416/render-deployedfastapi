from sqlalchemy import Table, Column, Integer, String, Text, Boolean, ARRAY, TIMESTAMP, ForeignKey
from database import metadata

users = Table(
    "users",
    metadata,
    Column("user_id", Integer, primary_key=True),
    Column("email", Text, nullable=True, unique=True),   # 🔷 made nullable
    Column("code", Text, unique=True),
    Column("hashed_password", Text, nullable=False),
    Column("role", Text, nullable=False),
    Column("phone", Text, nullable=True, unique=True),   # 🔷 made nullable
    Column("tenant_id", Integer, ForeignKey("tenant.tenant_id", ondelete="SET NULL")),
    Column("first_name", Text, nullable=False),
    Column("last_name", Text, nullable=False),
    Column("is_active", Boolean, default=True),
    Column("permissions", ARRAY(Text)),
    Column("created_by", Integer, ForeignKey("users.user_id", ondelete="SET NULL")),
    Column("updated_by", Integer, ForeignKey("users.user_id", ondelete="SET NULL")),
    Column("created_at", TIMESTAMP, nullable=False),
    Column("updated_at", TIMESTAMP, nullable=False)
)
