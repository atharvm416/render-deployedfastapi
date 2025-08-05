from datetime import datetime
from database import database
from models.users import users
from schemas.userschema import UserCreate, UserUpdate, User
from functions.generateId import generate_code
from functions.passwordhashing import hash_password, verify_password
from typing import Optional
from sqlalchemy import and_, select, func, desc, or_




async def create_user(data: UserCreate) -> Optional[User]:
    hashed_pw = hash_password(data.password)

    insert_query = users.insert().values(
        email=data.email,
        hashed_password=hashed_pw,
        role=data.role,
        tenant_id=data.tenant_id,
        phone=data.phone,
        first_name=data.first_name,
        last_name=data.last_name,
        is_active=data.is_active,
        permissions=data.permissions,
        created_by=data.created_by,
        updated_by=data.created_by,
    )
    user_id = await database.execute(insert_query)

    code = generate_code("USR", user_id)
    await database.execute(
        users.update().where(users.c.user_id == user_id).values(code=code)
    )

    row = await database.fetch_one(users.select().where(users.c.user_id == user_id))
    return User(**row) if row else None


async def get_user(user_id: int) -> Optional[User]:
    row = await database.fetch_one(users.select().where(users.c.user_id == user_id))
    return User(**row) if row else None


async def get_all_users() -> list[User]:
    records = await database.fetch_all(users.select())
    return [User(**r) for r in records]


async def update_user(user_id: int, data: UserUpdate) -> Optional[User]:
    update_data = data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    await database.execute(
        users.update().where(users.c.user_id == user_id).values(**update_data)
    )

    return await get_user(user_id)


async def delete_user(user_id: int) -> bool:
    result = await database.execute(
        users.delete().where(users.c.user_id == user_id)
    )
    return bool(result)


async def authenticate_user_by_email(email: str, password: str) -> Optional[User]: 
    user = await database.fetch_one(users.select().where(users.c.email == email))
    if user and verify_password(password, user['hashed_password']):
        return User(**user)
    return None


async def authenticate_user_by_phone(phone: str, password: str) -> Optional[User]:
    user = await database.fetch_one(users.select().where(users.c.phone == phone))
    if user and verify_password(password, user['hashed_password']):
        return User(**user)
    return None

async def update_password(user_id: int, new_password: str) -> bool:
    # Check if user exists
    user = await database.fetch_one(users.select().where(users.c.user_id == user_id))
    if not user:
        return False  # user not found

    # Hash and update new password
    hashed_pw = hash_password(new_password)
    await database.execute(
        users.update()
        .where(users.c.user_id == user_id)
        .values(hashed_password=hashed_pw, updated_at=datetime.utcnow())
    )

    return True

async def list_users_paginated(
    tenant_id: int,
    page: int = 1,
    page_size: int = 10,
    role: Optional[str] = None
) -> dict:
    page = max(1, page)
    offset = (page - 1) * page_size

    filters = [users.c.tenant_id == tenant_id]

    if role:
        filters.append(users.c.role == role)

    count_query = select(func.count()).select_from(users).where(and_(*filters))
    total = await database.fetch_val(count_query)

    query = (
        users.select()
        .where(and_(*filters))
        .order_by(desc(users.c.updated_at))
        .offset(offset)
        .limit(page_size)
    )

    records = await database.fetch_all(query)

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [User(**r) for r in records],
    }

async def list_users_by_role(role: str) -> list[User]:
    query = users.select().where(users.c.role == role)
    records = await database.fetch_all(query)
    return [User(**r) for r in records]

async def search_users(
    query: Optional[str],
    tenant_id: int,
    limit: int = 5
) -> list[User]:
    filters = [users.c.tenant_id == tenant_id]

    if query:
        search_term = f"%{query.lower()}%"
        filters.append(
            or_(
                func.lower(users.c.first_name).like(search_term),
                func.lower(users.c.last_name).like(search_term)
            )
        )

    sql_query = (
        users.select()
        .where(and_(*filters))
        .order_by(users.c.first_name.asc(), users.c.last_name.asc())
        .limit(limit)
    )

    records = await database.fetch_all(sql_query)
    return [User(**r) for r in records]
