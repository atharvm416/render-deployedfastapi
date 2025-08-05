# services/eventservice.py
from database import database
from models.event import event
from models.event_contact import event_contact
from sqlalchemy import func, select, desc, and_
from schemas.eventschema import EventCreate, EventUpdate, EventOut
from schemas.eventcontactschema import EventContactOut, EventContactCreate
from functions.generateId import generate_code
from services.eventcontactservice import create_event_contact
from sqlalchemy.orm import aliased
from models.users import users 
from models.space import space
from typing import Optional, List

async def create_event(data: EventCreate) -> EventOut | None:
    # Insert the event
    insert_query = event.insert().values(
        **data.dict(),
        updated_by=data.created_by
    )
    event_id = await database.execute(insert_query)

    # Generate and update event code
    code = generate_code("EVT", event_id)
    await database.execute(
        event.update().where(event.c.event_id == event_id).values(code=code)
    )

    # Create primary contact for the event
    contact_data = EventContactCreate(
        event_id=event_id,
        contact_type="organizer",   # or "primary", your choice
        contact_name=None,          # or some sensible default
        contact_email=None,
        contact_phone=None
    )
    await create_event_contact(contact_data)

    # Fetch and return the complete event
    return await get_event(event_id)


async def get_event(event_id: int) -> EventOut | None:
    row = await database.fetch_one(
        event.select().where(event.c.event_id == event_id)
    )
    return EventOut(**row) if row else None

async def update_event(event_id: int, data: EventUpdate) -> EventOut | None:
    await database.execute(
        event.update()
        .where(event.c.event_id == event_id)
        .values(**data.dict(exclude_unset=True))
    )
    return await get_event(event_id)

async def delete_event(event_id: int) -> bool:
    result = await database.execute(
        event.delete().where(event.c.event_id == event_id)
    )
    return bool(result)

async def list_events_paginated(
    tenant_id: int,
    page: int = 1,
    page_size: int = 10,
    status: str = None
) -> dict:
    page = max(page, 1)

    filters = [event.c.tenant_id == tenant_id]
    if status:
        filters.append(event.c.status == status)

    # total count
    count_query = select(func.count()).select_from(event).where(and_(*filters))
    total = await database.fetch_val(count_query)

    offset = (page - 1) * page_size

    # define aliases for users (creator + updater)
    created_user = aliased(users)
    updated_user = aliased(users)

    # join space too
    space_tbl = aliased(space)

    # query with joins
    query = (
        select(
            event,
            (created_user.c.first_name + ' ' + created_user.c.last_name).label("created_user"),
            (updated_user.c.first_name + ' ' + updated_user.c.last_name).label("updated_user"),
            space_tbl.c.label.label("space_label")
        )
        .select_from(
            event
            .outerjoin(created_user, event.c.created_by == created_user.c.user_id)
            .outerjoin(updated_user, event.c.updated_by == updated_user.c.user_id)
            .outerjoin(space_tbl, event.c.space_id == space_tbl.c.space_id)  # adjust FK if needed
        )
        .where(and_(*filters))
        .order_by(desc(event.c.updated_at))
        .offset(offset)
        .limit(page_size)
    )

    records = await database.fetch_all(query)

    # build event list
    events = []
    for r in records:
        e = dict(r)
        # fallback to None if no user or space found
        e["created_user"] = e.get("created_user") or None
        e["updated_user"] = e.get("updated_user") or None
        e["space_label"] = e.get("space_label") or None
        events.append(e)

    # fetch & attach contacts
    if events:
        event_ids = [e["event_id"] for e in events]

        contacts_query = (
            event_contact
            .select()
            .where(event_contact.c.event_id.in_(event_ids))
        )

        contacts_records = await database.fetch_all(contacts_query)

        # group contacts by event_id
        contacts_by_event = {}
        for c in contacts_records:
            contact = EventContactOut(**c).dict()
            contacts_by_event.setdefault(c["event_id"], []).append(contact)

        # attach contacts to events
        for ev in events:
            ev["contacts"] = contacts_by_event.get(ev["event_id"], [])
    else:
        events = []

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": events
    }


async def search_events(query: Optional[str], tenant_id: int, limit: int = 5) -> List[EventOut]:
    filters = [event.c.tenant_id == tenant_id]

    if query:
        filters.append(event.c.title.ilike(f"%{query}%"))

    q = (
        select(event)
        .where(and_(*filters))
        .order_by(event.c.updated_at.desc())
        .limit(limit)
    )

    records = await database.fetch_all(q)

    return [EventOut(**r) for r in records]