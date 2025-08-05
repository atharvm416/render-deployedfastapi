from database import database
from models.space import space
from schemas.spaceschema import SpaceCreate, SpaceUpdate, Space
from typing import Optional, List
from datetime import datetime
from functions.generateId import generate_code
from sqlalchemy import func, select, and_

async def create_space(data: SpaceCreate) -> Optional[Space]:
    insert_query = space.insert().values(
        label=data.label,
        type=data.type,
        capacity=data.capacity,
        status=data.status,
        tenant_id=data.tenant_id,
        created_by=data.created_by,
        updated_by=data.created_by
    )
    space_id = await database.execute(insert_query)

    code = generate_code("SPC", space_id)
    await database.execute(space.update().where(space.c.space_id == space_id).values(code=code))

    row = await database.fetch_one(space.select().where(space.c.space_id == space_id))
    return Space(**row) if row else None

async def get_space(space_id: int, tenant_id: int) -> Optional[Space]:
    row = await database.fetch_one(
        space.select().where(space.c.space_id == space_id).where(space.c.tenant_id == tenant_id)
    )
    return Space(**row) if row else None

async def get_spaces(tenant_id: int, page: int, page_size: int) -> List[Space]:
    offset = (page - 1) * page_size
    rows = await database.fetch_all(
        space.select()
        .where(space.c.tenant_id == tenant_id)
        .offset(offset)
        .limit(page_size)
    )
    return [Space(**r) for r in rows]

async def count_spaces(tenant_id: int) -> int:
    count_query = select(func.count()).where(space.c.tenant_id == tenant_id)
    return await database.fetch_val(count_query)


async def get_spaces(tenant_id: int, page: int = 1, page_size: int = 10) -> list[dict]:
    page = max(page, 1)
    offset = (page - 1) * page_size

    query = (
        space.select()
        .where(space.c.tenant_id == tenant_id)
        .order_by(space.c.updated_at.desc())  # 👈 order by updated_at DESC
        .limit(page_size)
        .offset(offset)
    )

    records = await database.fetch_all(query)
    return [dict(r) for r in records]

async def update_space(space_id: int, data: SpaceUpdate) -> Optional[Space]:
    update_data = data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    await database.execute(
        space.update()
        .where(space.c.space_id == space_id)
        .values(**update_data)
    )

    return await get_space_by_id(space_id)

async def delete_space(space_id: int) -> bool:
    result = await database.execute(
        space.delete().where(space.c.space_id == space_id)
    )
    return bool(result)

async def get_space_by_id(space_id: int) -> Optional[Space]:
    row = await database.fetch_one(space.select().where(space.c.space_id == space_id))
    return Space(**row) if row else None


async def get_all_spaces_for_tenant(tenant_id: int) -> list[dict]:
    """
    Fetch all spaces belonging to a given tenant_id, no pagination.
    Ordered by updated_at DESC.
    """
    query = (
        space.select()
        .where(space.c.tenant_id == tenant_id)
        .order_by(space.c.updated_at.desc())
    )

    rows = await database.fetch_all(query)
    return [dict(row) for row in rows]

async def search_spaces(query: Optional[str], tenant_id: int, limit: int = 5) -> List[Space]:
    filters = [space.c.tenant_id == tenant_id]

    if query:
        filters.append(space.c.label.ilike(f"%{query}%"))

    q = (
        select(space)
        .where(and_(*filters))
        .order_by(space.c.updated_at.desc())
        .limit(limit)
    )

    records = await database.fetch_all(q)

    return [Space(**r) for r in records]