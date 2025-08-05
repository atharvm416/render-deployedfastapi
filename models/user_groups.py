from sqlalchemy import Table, Column, Integer, Text, ARRAY, ForeignKey, TIMESTAMP, CheckConstraint
from database import metadata

user_groups = Table(
    "user_groups",
    metadata,
    Column("user_group_id", Integer, primary_key=True),
    Column("name", Text, nullable=False),
    Column("code", Text, nullable=True),  # 🔷 New column
    Column("description", Text, nullable=True),
    Column("tenant_id", Integer, ForeignKey("tenant.tenant_id", ondelete="CASCADE"), nullable=False),
    Column("member_ids", ARRAY(Integer), nullable=False),
    Column("status", Text, nullable=False, default='active'),
    Column("created_by", Integer, ForeignKey("users.user_id", ondelete="SET NULL")),
    Column("updated_by", Integer, ForeignKey("users.user_id", ondelete="SET NULL")),
    Column("created_at", TIMESTAMP, nullable=False),
    Column("updated_at", TIMESTAMP, nullable=False),
    CheckConstraint("status IN ('active', 'inactive', 'archived')", name="valid_status")
)
