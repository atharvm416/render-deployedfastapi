from sqlalchemy import Table, Column, Integer, String, Text, ForeignKey, CheckConstraint, TIMESTAMP, MetaData

metadata = MetaData()

space = Table(
    "space",
    metadata,
    Column("space_id", Integer, primary_key=True),
    Column("label", Text, nullable=False),
    Column("code", Text, unique=True),
    Column("type", Text, nullable=False),
    Column("capacity", Integer),
    Column("status", Text),
    Column("tenant_id", Integer, ForeignKey("tenant.tenant_id", ondelete="SET NULL")),
    Column("created_by", Integer, ForeignKey("users.user_id", ondelete="SET NULL")),
    Column("updated_by", Integer, ForeignKey("users.user_id", ondelete="SET NULL")),
    Column("created_at", TIMESTAMP, server_default="now()"),
    Column("updated_at", TIMESTAMP, server_default="now()"),
    CheckConstraint("capacity >= 0", name="check_capacity_positive"),
    CheckConstraint("type IN ('building', 'room', 'area', 'zone', 'warehouse')", name="check_type_valid"),
    CheckConstraint("status IN ('active', 'under_maintenance', 'closed')", name="check_status_valid")
)
