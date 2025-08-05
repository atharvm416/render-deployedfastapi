from sqlalchemy import Table, Column, Integer, Text, TIMESTAMP
from database import metadata

tenant = Table(
    "tenant",
    metadata,
    Column("tenant_id", Integer, primary_key=True),  # Changed from String to Integer
    Column("code", Text, unique=True),               # If you're using 'code' field (optional)
    Column("name", Text, nullable=False),
    Column("contact_email", Text),
    Column("contact_name", Text),
    Column("phone", Text),
    Column("address", Text),
    Column("created_at", TIMESTAMP, nullable=False),
    Column("updated_at", TIMESTAMP, nullable=False),
)
