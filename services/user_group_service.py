from datetime import datetime
from database import database
from models.user_groups import user_groups
from models.users import users
from schemas.usergroupschema import UserGroupCreate, UserGroupUpdate, UserGroup
from functions.generateId import generate_code
from typing import Optional, List
from sqlalchemy import and_, select, func, desc


async def create_user_group(data: UserGroupCreate) -> Optional[UserGroup]:
    now = datetime.utcnow()

    insert_query = user_groups.insert().values(
        name=data.name,
        code="",  # will be updated after insert
        description=data.description,
        tenant_id=data.tenant_id,
        member_ids=data.member_ids,
        status=data.status,
        created_by=data.created_by,
        updated_by=data.created_by,
        created_at=now,
        updated_at=now,
    )

    user_group_id = await database.execute(insert_query)

    code = generate_code("UGR", user_group_id)
    await database.execute(
        user_groups.update().where(user_groups.c.user_group_id == user_group_id).values(code=code)
    )

    row = await database.fetch_one(user_groups.select().where(user_groups.c.user_group_id == user_group_id))
    return UserGroup(**row) if row else None


async def get_user_group(user_group_id: int) -> Optional[UserGroup]:
    row = await database.fetch_one(user_groups.select().where(user_groups.c.user_group_id == user_group_id))
    return UserGroup(**row) if row else None


async def get_all_user_groups() -> List[UserGroup]:
    rows = await database.fetch_all(user_groups.select())
    return [UserGroup(**r) for r in rows]


async def update_user_group(user_group_id: int, data: UserGroupUpdate) -> Optional[UserGroup]:
    update_data = data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    await database.execute(
        user_groups.update().where(user_groups.c.user_group_id == user_group_id).values(**update_data)
    )

    return await get_user_group(user_group_id)


async def delete_user_group(user_group_id: int) -> bool:
    result = await database.execute(
        user_groups.delete().where(user_groups.c.user_group_id == user_group_id)
    )
    return bool(result)


async def list_user_groups_paginated(
    tenant_id: int,
    page: int = 1,
    page_size: int = 10,
    status: Optional[str] = None,
) -> dict:
    offset = (page - 1) * page_size
    filters = [user_groups.c.tenant_id == tenant_id]
    if status:
        filters.append(user_groups.c.status == status)

    # Count total groups
    count_query = select(func.count()).select_from(user_groups).where(and_(*filters))
    total = await database.fetch_val(count_query)

    # Fetch paginated groups
    query = (
        select(user_groups)
        .where(and_(*filters))
        .order_by(desc(user_groups.c.updated_at))
        .offset(offset)
        .limit(page_size)
    )
    records = await database.fetch_all(query)

    enriched_groups = []

    for record in records:
        group_dict = dict(record)
        member_ids = group_dict.get("member_ids", [])
        
        # Members
        members = []
        if member_ids:
            member_query = (
                select(
                    users.c.user_id,
                    users.c.first_name,
                    users.c.last_name
                )
                .where(users.c.user_id.in_(member_ids))
            )
            member_results = await database.fetch_all(member_query)
            members = [{"user_id": r["user_id"], "first_name": r["first_name"], "last_name": r["last_name"]} for r in member_results]
        group_dict["members"] = members

        # created_user
        created_user = await database.fetch_one(
            select(users.c.first_name, users.c.last_name)
            .where(users.c.user_id == group_dict.get("created_by"))
        )
        group_dict["created_user"] = f"{created_user['first_name']} {created_user['last_name']}" if created_user else None

        # updated_user
        updated_user = await database.fetch_one(
            select(users.c.first_name, users.c.last_name)
            .where(users.c.user_id == group_dict.get("updated_by"))
        )
        group_dict["updated_user"] = f"{updated_user['first_name']} {updated_user['last_name']}" if updated_user else None

        enriched_groups.append(group_dict)

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": enriched_groups
    }


async def search_user_groups(
    query: Optional[str],
    tenant_id: int,
    limit: int = 5
) -> List[dict]:
    filters = [user_groups.c.tenant_id == tenant_id]

    if query:
        search_term = f"%{query.lower()}%"
        filters.append(func.lower(user_groups.c.name).like(search_term))

    sql_query = (
        user_groups.select()
        .where(and_(*filters))
        .order_by(user_groups.c.name.asc())
        .limit(limit)
    )

    rows = await database.fetch_all(sql_query)

    result = []
    for row in rows:
        group = dict(row)

        # Members
        member_ids = group.get("member_ids", [])
        members = []
        if member_ids:
            member_rows = await database.fetch_all(
                users.select().where(users.c.user_id.in_(member_ids))
            )
            members = [
                {
                    "user_id": m["user_id"],
                    "first_name": m["first_name"],
                    "last_name": m["last_name"],
                }
                for m in member_rows
            ]

        group["members"] = members
        group.pop("member_ids", None)

        # created_user
        created_user = await database.fetch_one(
            select(users.c.first_name, users.c.last_name)
            .where(users.c.user_id == group.get("created_by"))
        )
        group["created_user"] = f"{created_user['first_name']} {created_user['last_name']}" if created_user else None

        # updated_user
        updated_user = await database.fetch_one(
            select(users.c.first_name, users.c.last_name)
            .where(users.c.user_id == group.get("updated_by"))
        )
        group["updated_user"] = f"{updated_user['first_name']} {updated_user['last_name']}" if updated_user else None

        result.append(group)

    return result
