from models.assets import asset
from database import database
from schemas.assetsschema import AssetCreate, AssetUpdate, AssetOut
from sqlalchemy import func, select, desc, and_
from functions.generateId import generate_code
from typing import Optional, List
from sqlalchemy.orm import aliased
from models.space import space

async def create_asset(data: AssetCreate) -> AssetOut | None:
    insert_query = asset.insert().values(
        name=data.name,
        category=data.category,
        serial_number=data.serial_number,
        space_id=data.space_id,
        tenant_id=data.tenant_id,
        status=data.status,
        created_by=data.created_by,
        updated_by=data.created_by 
    )
    asset_id = await database.execute(insert_query)

    code = generate_code("AST", asset_id)
    update_query = asset.update().where(asset.c.asset_id == asset_id).values(code=code)
    await database.execute(update_query)

    return await get_asset(asset_id)


async def get_asset(asset_id: int) -> AssetOut | None:
    query = asset.select().where(asset.c.asset_id == asset_id)
    record = await database.fetch_one(query)
    if record:
        return AssetOut(**record)
    return None


async def get_all_assets() -> list[AssetOut]:
    query = asset.select()
    records = await database.fetch_all(query)
    return [AssetOut(**r) for r in records]


async def update_asset(asset_id: int, data: AssetUpdate) -> AssetOut | None:
    query = (
        asset.update()
        .where(asset.c.asset_id == asset_id)
        .values(**data.dict(exclude_unset=True))
    )
    await database.execute(query)

    updated = await get_asset(asset_id)
    return updated


async def delete_asset(asset_id: int) -> bool:
    # Check if asset exists
    exists_query = asset.select().where(asset.c.asset_id == asset_id)
    record = await database.fetch_one(exists_query)
    if not record:
        return False

    # Proceed to delete
    await database.execute(
        asset.delete().where(asset.c.asset_id == asset_id)
    )
    return True


async def list_assets_paginated(
    tenant_id: int,
    page: int = 1,
    page_size: int = 10,
    status: str = "all"
) -> dict:
    page = max(page, 1)

    filters = [asset.c.tenant_id == tenant_id]
    if status != "all":
        filters.append(asset.c.status == status)

    # total count
    count_query = select(func.count()).select_from(asset).where(and_(*filters))
    total = await database.fetch_val(count_query)

    offset = (page - 1) * page_size

    # alias for space table
    space_tbl = aliased(space)

    # main query with space join
    query = (
        select(
            asset,
            space_tbl.c.label.label("space_label")
        )
        .select_from(
            asset.outerjoin(space_tbl, asset.c.space_id == space_tbl.c.space_id)
        )
        .where(and_(*filters))
        .order_by(desc(asset.c.updated_at))
        .offset(offset)
        .limit(page_size)
    )

    records = await database.fetch_all(query)

    # convert to dict and handle missing space_label
    items = []
    for r in records:
        row = dict(r)
        row["space_label"] = row.get("space_label") or None
        items.append(row)

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }

async def search_assets(query: Optional[str], tenant_id: int, limit: int = 5) -> List[AssetOut]:
    filters = [asset.c.tenant_id == tenant_id]

    if query:
        filters.append(asset.c.name.ilike(f"%{query}%"))

    q = (
        select(asset)
        .where(and_(*filters))
        .order_by(asset.c.updated_at.desc())
        .limit(limit)
    )

    records = await database.fetch_all(q)

    return [AssetOut(**r) for r in records]