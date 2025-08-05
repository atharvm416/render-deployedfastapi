# services/projectservice.py
from database import database
from models.project import project
from schemas.projectschema import ProjectCreate, ProjectUpdate, ProjectOut
from schemas.project_contactschema import ProjectContactCreate, ProjectContactOut
from services.project_contactservice import create_contact
from models.project_contact import project_contact
from sqlalchemy import func, select, and_, desc
from datetime import datetime
from functions.generateId import generate_code
from typing import Optional, List
from sqlalchemy.orm import aliased
from models.users import users

async def create_project(data: ProjectCreate) -> ProjectOut | None:
    # Insert project
    insert_query = project.insert().values(
        **data.dict(),
        updated_by=data.created_by
    )
    project_id = await database.execute(insert_query)

    # Generate and update project code
    code = generate_code("PRJ", project_id)
    await database.execute(
        project.update().where(project.c.project_id == project_id).values(code=code)
    )

    # Optional: fetch the project now
    project_obj = await get_project(project_id)

    # Create primary contact
    contact_data = ProjectContactCreate(
        project_id=project_id,
        contact_type="primary",
        contact_name=None,  # Or some sensible default
        contact_email=None,
        contact_phone=None
    )
    await create_contact(contact_data)

    return project_obj

async def get_project(project_id: int) -> ProjectOut | None:
    row = await database.fetch_one(project.select().where(project.c.project_id == project_id))
    return ProjectOut(**row) if row else None

async def update_project(project_id: int, data: ProjectUpdate) -> ProjectOut | None:
    update_data = data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    await database.execute(
        project.update()
        .where(project.c.project_id == project_id)
        .values(**update_data)
    )

    return await get_project(project_id)

async def delete_project(project_id: int) -> bool:
    result = await database.execute(
        project.delete().where(project.c.project_id == project_id)
    )
    return bool(result)

async def list_projects_paginated(
    tenant_id: int,
    page: int = 1,
    page_size: int = 10,
    project_type: str = None,
    status: str = None,
    priority: str = None
) -> dict:
    page = max(page, 1)

    filters = [project.c.tenant_id == tenant_id]

    if project_type:
        filters.append(project.c.project_type == project_type)

    if status:
        filters.append(project.c.status == status)

    if priority:
        filters.append(project.c.priority == priority)

    # total count
    count_query = select(func.count()).select_from(project).where(and_(*filters))
    total = await database.fetch_val(count_query)

    offset = (page - 1) * page_size

    # aliases for users
    created_user = aliased(users)
    updated_user = aliased(users)

    # query with joins for created & updated users
    query = (
        select(
            project,
            (created_user.c.first_name + ' ' + created_user.c.last_name).label("created_user"),
            (updated_user.c.first_name + ' ' + updated_user.c.last_name).label("updated_user")
        )
        .select_from(
            project
            .outerjoin(created_user, project.c.created_by == created_user.c.user_id)
            .outerjoin(updated_user, project.c.updated_by == updated_user.c.user_id)
        )
        .where(and_(*filters))
        .order_by(desc(project.c.updated_at))
        .offset(offset)
        .limit(page_size)
    )

    records = await database.fetch_all(query)

    projects = []
    for r in records:
        p = dict(r)
        # fallback to None if no user found
        p["created_user"] = p.get("created_user") or None
        p["updated_user"] = p.get("updated_user") or None
        projects.append(p)

    # fetch & attach contacts
    if projects:
        project_ids = [p["project_id"] for p in projects]

        contacts_query = (
            project_contact
            .select()
            .where(project_contact.c.project_id.in_(project_ids))
        )

        contacts_records = await database.fetch_all(contacts_query)

        # group contacts by project_id
        contacts_by_project = {}
        for c in contacts_records:
            contact = ProjectContactOut(**c).dict()
            contacts_by_project.setdefault(c["project_id"], []).append(contact)

        # attach contacts
        for proj in projects:
            proj["contacts"] = contacts_by_project.get(proj["project_id"], [])
    else:
        projects = []

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": projects
    }

async def search_projects(query: Optional[str], tenant_id: int, limit: int = 5) -> List[ProjectOut]:
    filters = [project.c.tenant_id == tenant_id]

    if query:
        filters.append(project.c.name.ilike(f"%{query}%"))

    q = (
        select(project)
        .where(and_(*filters))
        .order_by(project.c.updated_at.desc())
        .limit(limit)
    )

    records = await database.fetch_all(q)

    return [ProjectOut(**r) for r in records]