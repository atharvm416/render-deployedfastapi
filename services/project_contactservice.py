# services/project_contactservice.py
from database import database
from models.project_contact import project_contact
from schemas.project_contactschema import (
    ProjectContactCreate, ProjectContactUpdate, ProjectContactOut
)

async def create_contact(data: ProjectContactCreate) -> ProjectContactOut | None:
    insert_query = project_contact.insert().values(**data.dict())
    contact_id = await database.execute(insert_query)
    return await get_contact(contact_id)

async def get_contact(contact_id: int) -> ProjectContactOut | None:
    row = await database.fetch_one(
        project_contact.select().where(project_contact.c.contact_id == contact_id)
    )
    return ProjectContactOut(**row) if row else None

async def update_contact(contact_id: int, data: ProjectContactUpdate) -> ProjectContactOut | None:
    await database.execute(
        project_contact.update()
        .where(project_contact.c.contact_id == contact_id)
        .values(**data.dict(exclude_unset=True))
    )
    return await get_contact(contact_id)

async def delete_contact(contact_id: int) -> bool:
    result = await database.execute(
        project_contact.delete().where(project_contact.c.contact_id == contact_id)
    )
    return bool(result)
