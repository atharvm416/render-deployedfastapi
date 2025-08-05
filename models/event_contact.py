# models/event_contact.py
from sqlalchemy import Table, Column, Integer, String, Text, ForeignKey, MetaData

metadata = MetaData()

event_contact = Table(
    "event_contacts",
    metadata,
    Column("contact_id", Integer, primary_key=True),
    Column("event_id", Integer, ForeignKey("event.event_id", ondelete="CASCADE")),
    Column("contact_type", String),
    Column("contact_name", Text, nullable=False),
    Column("contact_email", String),
    Column("contact_phone", String),
)
