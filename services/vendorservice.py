from database import database
from models.vendor import vendor
from schemas.vendorschema import VendorCreate, VendorUpdate, VendorOut
from sqlalchemy import func, select, desc, and_
from functions.generateId import generate_code
from typing import Optional, List


async def create_vendor(data: VendorCreate) -> VendorOut | None:
    insert_query = vendor.insert().values(
        **data.dict(),
        updated_by=data.created_by
    )
    vendor_id = await database.execute(insert_query)

    code = generate_code("VND", vendor_id)
    await database.execute(
        vendor.update()
        .where(vendor.c.vendor_id == vendor_id)
        .values(code=code)
    )

    return await get_vendor(vendor_id)


async def get_vendor(vendor_id: int) -> VendorOut | None:
    query = vendor.select().where(vendor.c.vendor_id == vendor_id)
    record = await database.fetch_one(query)
    if record:
        return VendorOut(**record)
    return None


async def update_vendor(vendor_id: int, data: VendorUpdate) -> VendorOut | None:
    await database.execute(
        vendor.update()
        .where(vendor.c.vendor_id == vendor_id)
        .values(**data.dict(exclude_unset=True))
    )
    return await get_vendor(vendor_id)


async def delete_vendor(vendor_id: int) -> bool:
    exists_query = vendor.select().where(vendor.c.vendor_id == vendor_id)
    record = await database.fetch_one(exists_query)
    if not record:
        return False

    await database.execute(
        vendor.delete().where(vendor.c.vendor_id == vendor_id)
    )
    return True


async def list_vendors_paginated(
    tenant_id: int,
    page: int = 1,
    page_size: int = 10,
    status: str = "all",
    vendor_type: str = None,
    compliance_status: str = None,
    payment_terms: str = None
) -> dict:
    page = max(page, 1)

    filters = [vendor.c.tenant_id == tenant_id]

    if status != "all":
        filters.append(vendor.c.status == status)

    if vendor_type:
        filters.append(vendor.c.vendor_type == vendor_type)

    if compliance_status:
        filters.append(vendor.c.compliance_status == compliance_status)

    if payment_terms:
        filters.append(vendor.c.payment_terms == payment_terms)

    # count query
    count_query = select(func.count()).select_from(vendor).where(and_(*filters))
    total = await database.fetch_val(count_query)

    offset = (page - 1) * page_size

    # data query
    query = (
        vendor.select()
        .where(and_(*filters))
        .order_by(desc(vendor.c.updated_at))
        .offset(offset)
        .limit(page_size)
    )

    records = await database.fetch_all(query)

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [dict(r) for r in records]
    }

async def search_vendors(query: Optional[str], tenant_id: int, limit: int = 5) -> List[VendorOut]:
    filters = [vendor.c.tenant_id == tenant_id]

    if query:
        filters.append(vendor.c.name.ilike(f"%{query}%"))

    q = (
        select(vendor)
        .where(and_(*filters))
        .order_by(vendor.c.updated_at.desc())
        .limit(limit)
    )

    records = await database.fetch_all(q)

    return [VendorOut(**r) for r in records]