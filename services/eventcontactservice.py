# services/eventcontactservice.py
from database import database
from models.event_contact import event_contact
from schemas.eventcontactschema import EventContactCreate, EventContactUpdate, EventContactOut

async def create_event_contact(data: EventContactCreate) -> EventContactOut | None:
    insert_query = event_contact.insert().values(**data.dict())
    contact_id = await database.execute(insert_query)
    return await get_event_contact(contact_id)

async def get_event_contact(contact_id: int) -> EventContactOut | None:
    row = await database.fetch_one(
        event_contact.select().where(event_contact.c.contact_id == contact_id)
    )
    return EventContactOut(**row) if row else None

async def update_event_contact(contact_id: int, data: EventContactUpdate) -> EventContactOut | None:
    await database.execute(
        event_contact.update()
        .where(event_contact.c.contact_id == contact_id)
        .values(**data.dict(exclude_unset=True))
    )
    return await get_event_contact(contact_id)

async def delete_event_contact(contact_id: int) -> bool:
    result = await database.execute(
        event_contact.delete().where(event_contact.c.contact_id == contact_id)
    )
    return bool(result)

async def list_event_contacts(event_id: int) -> list[dict]:
    rows = await database.fetch_all(
        event_contact.select().where(event_contact.c.event_id == event_id)
    )
    return [dict(r) for r in rows]
