# models/project_contact.py
from sqlalchemy import Table, Column, Integer, String, Text, ForeignKey, MetaData

metadata = MetaData()

project_contact = Table(
    "project_contacts",
    metadata,
    Column("contact_id", Integer, primary_key=True),
    Column("project_id", Integer, ForeignKey("project.project_id", ondelete="CASCADE")),
    Column("contact_type", String),
    Column("contact_name", Text),
    Column("contact_email", String),
    Column("contact_phone", String),
)
