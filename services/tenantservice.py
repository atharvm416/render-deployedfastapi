from models.tenant import tenant
from database import database
from schemas.tenantschema import TenantCreate, TenantUpdate, Tenant
from sqlalchemy import func, select, and_
from functions.generateId import generate_code
from models.assets import asset
from models.users import users
from models.event import event
from models.project import project
from models.space import space
from models.task import task
from models.vendor import vendor
from typing import List, Optional


async def create_tenant(data: TenantCreate) -> Tenant | None:
    insert_query = tenant.insert().values(
        name=data.name,
        contact_email=data.contact_email,
        contact_name=data.contact_name,
        phone=data.phone,
        address=data.address
    )
    tenant_id = await database.execute(insert_query)

    code = generate_code("TNT", tenant_id)
    update_query = tenant.update().where(tenant.c.tenant_id == tenant_id).values(code=code)
    await database.execute(update_query)

    return await get_tenant(tenant_id)


async def get_tenant(tenant_id: int) -> Tenant | None:
    query = tenant.select().where(tenant.c.tenant_id == tenant_id)
    record = await database.fetch_one(query)
    if record:
        return Tenant(**record)
    return None


async def get_all_tenants() -> list[Tenant]:
    query = tenant.select()
    records = await database.fetch_all(query)
    return [Tenant(**r) for r in records]


async def update_tenant(tenant_id: int, data: TenantUpdate) -> Tenant | None:
    query = (
        tenant.update()
        .where(tenant.c.tenant_id == tenant_id)
        .values(**data.dict(exclude_unset=True))
    )
    await database.execute(query)

    updated = await get_tenant(tenant_id)
    return updated


async def delete_tenant(tenant_id: int) -> bool:
    # Check if tenant exists
    exists_query = tenant.select().where(tenant.c.tenant_id == tenant_id)
    record = await database.fetch_one(exists_query)
    if not record:
        return False

    # Proceed to delete
    await database.execute(
        tenant.delete().where(tenant.c.tenant_id == tenant_id)
    )
    return True



async def list_tenants_paginated(page: int = 1, page_size: int = 10) -> dict:
    page = max(page, 1)

    count_query = select(func.count()).select_from(tenant)
    total = await database.fetch_val(count_query)

    offset = (page - 1) * page_size

    query = (
        tenant.select()
        .order_by(tenant.c.updated_at.desc())
        .limit(page_size)
        .offset(offset)
    )
    records = await database.fetch_all(query)
    tenants = [dict(r) for r in records]

    # fetch counts for each tenant
    for t in tenants:
        tid = t["tenant_id"]

        t["user_count"] = await database.fetch_val(
            select(func.count()).select_from(users).where(users.c.tenant_id == tid)
        )
        t["space_count"] = await database.fetch_val(
            select(func.count()).select_from(space).where(space.c.tenant_id == tid)
        )
        t["asset_count"] = await database.fetch_val(
            select(func.count()).select_from(asset).where(asset.c.tenant_id == tid)
        )
        t["vendor_count"] = await database.fetch_val(
            select(func.count()).select_from(vendor).where(vendor.c.tenant_id == tid)
        )
        t["event_count"] = await database.fetch_val(
            select(func.count()).select_from(event).where(event.c.tenant_id == tid)
        )
        t["project_count"] = await database.fetch_val(
            select(func.count()).select_from(project).where(project.c.tenant_id == tid)
        )
        t["task_count"] = await database.fetch_val(
            select(func.count()).select_from(task).where(task.c.tenant_id == tid)
        )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": tenants
    }

async def search_tenants(query: Optional[str], tenant_id: Optional[int] = None, limit: int = 5) -> List[Tenant]:
    filters = []

    if tenant_id is not None:
        filters.append(tenant.c.tenant_id == tenant_id)

    if query:
        filters.append(tenant.c.name.ilike(f"%{query}%"))

    q = (
        select(tenant)
        .where(and_(*filters)) if filters else select(tenant)
    ).order_by(tenant.c.updated_at.desc()).limit(limit)

    records = await database.fetch_all(q)
    return [Tenant(**r) for r in records]
