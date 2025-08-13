from models.task import task
from database import database
from schemas.taskschema import TaskCreate, TaskUpdate, TaskOut
from functions.generateId import generate_code
from sqlalchemy import select, and_, desc, func
from datetime import datetime, time
from typing import Optional
from sqlalchemy.orm import aliased
from models.users import users 
from models.project import project 
from models.assets import asset 
from models.vendor import vendor 
from models.space import space 
from models.event import event
from models.user_groups import user_groups
from dateutil.rrule import rrulestr
import re


def strip_tz(dt: Optional[datetime]) -> Optional[datetime]:
    if isinstance(dt, datetime) and dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt

async def create_task(data: TaskCreate) -> Optional[TaskOut]:
    # run through schema validation explicitly
    validated = TaskCreate(**data.dict())
    
    insert_query = task.insert().values(
        title=validated.title,
        description=validated.description,
        priority_level=validated.priority_level,
        status=validated.status,
        assigned_to=validated.assigned_to,
        manager_id=validated.manager_id,
        due_date=strip_tz(validated.due_date),
        related_vendor=validated.related_vendor,
        completion_notes=validated.completion_notes,
        completion_date=strip_tz(validated.completion_date),
        project_id=validated.project_id,
        event_id=validated.event_id,
        tenant_id=validated.tenant_id,
        event_phase=validated.event_phase,
        recurrence_rule=validated.recurrence_rule,
        recurrence_end_date=strip_tz(validated.recurrence_end_date),
        is_main_task=validated.is_main_task if validated.is_main_task is not None else False,
        user_group_id=validated.user_group_id,
        space_id=validated.space_id,
        asset_id=validated.asset_id,
        is_archived=validated.is_archived,
        archived_at=strip_tz(validated.archived_at),
        created_by=validated.created_by,
        updated_by=validated.created_by,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    task_id = await database.execute(insert_query)

    # update code properly
    code = generate_code("TASK", task_id)
    await database.execute(
        task.update().where(task.c.task_id == task_id).values(code=code)
    )

    row = await database.fetch_one(task.select().where(task.c.task_id == task_id))
    return TaskOut(**row) if row else None


async def get_task(task_id: int) -> TaskOut | None:
    row = await database.fetch_one(task.select().where(task.c.task_id == task_id))
    return TaskOut(**row) if row else None

async def update_task(task_id: int, data: TaskUpdate) -> TaskOut | None:
    update_data = data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    await database.execute(
        task.update().where(task.c.task_id == task_id).values(**update_data)
    )
    return await get_task(task_id)

async def delete_task(task_id: int) -> bool:
    result = await database.execute(
        task.delete().where(task.c.task_id == task_id)
    )
    return bool(result)

async def all_tasks() -> list[TaskOut]:
    rows = await database.fetch_all(task.select())
    return [TaskOut(**r) for r in rows]


async def list_tasks_paginated(
    tenant_id: int,
    page: int = 1,
    page_size: int = 10,
    status: Optional[str] = None,
    priority_level: Optional[str] = None,
    event_phase: Optional[str] = None,
    assigned_to: Optional[int] = None,
    manager_id: Optional[int] = None,
    project_id: Optional[int] = None,
    event_id: Optional[int] = None,
    related_vendor: Optional[int] = None,
    space_id: Optional[int] = None,
    asset_id: Optional[int] = None,
    is_archived: Optional[bool] = None,
    is_main_task: Optional[str] = None,  # ✅ new param, expects: "true", "false", "both" or None
    user_group_id: Optional[int] = None,
) -> dict:
    page = max(page, 1)
    offset = (page - 1) * page_size

    filters = [task.c.tenant_id == tenant_id]

    if status:
        filters.append(task.c.status == status)
    if priority_level:
        filters.append(task.c.priority_level == priority_level)
    if event_phase:
        filters.append(task.c.event_phase == event_phase)
    if assigned_to:
        filters.append(task.c.assigned_to == assigned_to)
    if manager_id:
        filters.append(task.c.manager_id == manager_id)
    if project_id:
        filters.append(task.c.project_id == project_id)
    if event_id:
        filters.append(task.c.event_id == event_id)
    if related_vendor:
        filters.append(task.c.related_vendor == related_vendor)
    if space_id:
        filters.append(task.c.space_id == space_id)
    if asset_id:
        filters.append(task.c.asset_id == asset_id)
    if is_archived is not None:
        filters.append(task.c.is_archived == is_archived)
    if user_group_id:
        filters.append(task.c.user_group_id == user_group_id)

    # ✅ New default behavior
    if is_main_task is None:
        # user didn’t specify → show only child tasks
        filters.append(task.c.is_main_task == False)
    elif is_main_task.lower() == "true":
        filters.append(task.c.is_main_task == True)
    elif is_main_task.lower() == "false":
        filters.append(task.c.is_main_task == False)
    # if user explicitly passes "both" or something else → no filter on is_main_task

    # COUNT query
    count_query = select(func.count()).select_from(task).where(and_(*filters))
    total = await database.fetch_val(count_query)

    # aliases etc remain the same …
    assigned_user = aliased(users)
    manager_user = aliased(users)
    vendor_tbl = aliased(vendor)
    project_tbl = aliased(project)
    event_tbl = aliased(event)
    space_tbl = aliased(space)
    asset_tbl = aliased(asset)
    parent_task_tbl = aliased(task)
    user_group_tbl = aliased(user_groups)

    query = (
        select(
            task,
            (assigned_user.c.first_name + ' ' + assigned_user.c.last_name).label("assigned_user_name"),
            (manager_user.c.first_name + ' ' + manager_user.c.last_name).label("manager_user_name"),
            vendor_tbl.c.name.label("vendor_name"),
            project_tbl.c.name.label("project_name"),
            event_tbl.c.title.label("event_title"),
            space_tbl.c.label.label("space_label"),
            asset_tbl.c.name.label("asset_name"),
            parent_task_tbl.c.title.label("parent_task_title"),
            user_group_tbl.c.name.label("user_group_name"),
        )
        .select_from(
            task
            .outerjoin(assigned_user, task.c.assigned_to == assigned_user.c.user_id)
            .outerjoin(manager_user, task.c.manager_id == manager_user.c.user_id)
            .outerjoin(vendor_tbl, task.c.related_vendor == vendor_tbl.c.vendor_id)
            .outerjoin(project_tbl, task.c.project_id == project_tbl.c.project_id)
            .outerjoin(event_tbl, task.c.event_id == event_tbl.c.event_id)
            .outerjoin(space_tbl, task.c.space_id == space_tbl.c.space_id)
            .outerjoin(asset_tbl, task.c.asset_id == asset_tbl.c.asset_id)
            .outerjoin(parent_task_tbl, task.c.parent_task_id == parent_task_tbl.c.task_id)
            .outerjoin(user_group_tbl, task.c.user_group_id == user_group_tbl.c.user_group_id)
        )
        .where(and_(*filters))
        .order_by(desc(task.c.updated_at))
        .offset(offset)
        .limit(page_size)
    )

    records = await database.fetch_all(query)

    tasks = []
    for r in records:
        task_data = dict(r)
        task_data["assigned_user"] = task_data.pop("assigned_user_name", None)
        task_data["manager_user"] = task_data.pop("manager_user_name", None)
        task_data["vendor_name"] = task_data.pop("vendor_name", None)
        task_data["project_name"] = task_data.pop("project_name", None)
        task_data["event_title"] = task_data.pop("event_title", None)
        task_data["space_label"] = task_data.pop("space_label", None)
        task_data["asset_name"] = task_data.pop("asset_name", None)
        task_data["parent_task_title"] = task_data.pop("parent_task_title", None)
        tasks.append(task_data)

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": tasks
    }


async def get_all_tasks_by_tenant(tenant_id: int) -> list[TaskOut]:
    """
    Fetch all tasks for a given tenant_id (no pagination)
    """
    query = task.select().where(task.c.tenant_id == tenant_id).order_by(desc(task.c.updated_at))
    rows = await database.fetch_all(query)
    return [TaskOut(**row) for row in rows]

async def create_task_with_recurrence(data: TaskCreate) -> Optional[TaskOut]:
    validated = TaskCreate(**data.dict())
    now = datetime.utcnow()

    # =========================
    # Determine due dates etc.
    # =========================
    parent_due_date = validated.due_date or now
    start_date = parent_due_date
    recurrence_end_date = validated.recurrence_end_date

    # ==================================
    # Insert the parent (main) task
    # ==================================
    parent_task_id = await database.execute(
        task.insert().values(
            title=validated.title,
            description=validated.description,
            priority_level=validated.priority_level,
            status=validated.status,
            assigned_to=validated.assigned_to,
            manager_id=validated.manager_id,
            related_vendor=validated.related_vendor,
            completion_notes=validated.completion_notes,
            completion_date=strip_tz(validated.completion_date),
            project_id=validated.project_id,
            event_id=validated.event_id,
            tenant_id=validated.tenant_id,
            event_phase=validated.event_phase,
            recurrence_rule=validated.recurrence_rule,
            recurrence_end_date=strip_tz(recurrence_end_date),
            due_date=strip_tz(recurrence_end_date),
            is_main_task=True,
            user_group_id=validated.user_group_id,
            space_id=validated.space_id,
            asset_id=validated.asset_id,
            is_archived=validated.is_archived,
            archived_at=strip_tz(validated.archived_at),
            created_by=validated.created_by,
            updated_by=validated.created_by,
            created_at=now,
            updated_at=now
        )
    )

    parent_code = generate_code("TASK", parent_task_id)
    await database.execute(
        task.update().where(task.c.task_id == parent_task_id).values(code=parent_code)
    )

    parent_row = await database.fetch_one(
        task.select().where(task.c.task_id == parent_task_id)
    )
    parent_task = TaskOut(**parent_row) if parent_row else None

    # =====================================
    # If no recurrence rule, we are done
    # =====================================
    if not validated.recurrence_rule or not recurrence_end_date:
        return parent_task

    # ===============================================
    # Ensure RRULE UNTIL is accurate & end of day
    # ===============================================
    # Clean "Z" at the end (dateutil expects no trailing Z for naive local times)
    recurrence_rule_clean = re.sub(
        r'UNTIL=([0-9T]+)Z',
        r'UNTIL=\1',
        validated.recurrence_rule
    )

    # If recurrence_end_date is date-only or time is at midnight, set to end-of-day
    if isinstance(recurrence_end_date, datetime) and recurrence_end_date.time() == time(0, 0):
        recurrence_end_date = recurrence_end_date.replace(hour=23, minute=59, second=59)

    # Replace UNTIL in RRULE to match recurrence_end_date (full date+time)
    if recurrence_end_date:
        until_value = recurrence_end_date.strftime("%Y%m%dT%H%M%S")
        # Replace any existing UNTIL (with or without T/hhmmss)
        recurrence_rule_clean = re.sub(
            r'UNTIL=\d{8}(T\d{6})?',
            f'UNTIL={until_value}',
            recurrence_rule_clean
        )

    # Build rrule string with DTSTART
    rrule_str = "DTSTART:{0}\nRRULE:{1}".format(
        start_date.strftime('%Y%m%dT%H%M%S'), recurrence_rule_clean
    )

    try:
        rule = rrulestr(rrule_str, dtstart=start_date)
        occurrences = list(rule)
    except Exception as e:
        print(f"Failed to parse RRULE: {e}")
        return parent_task

    # ===========================
    # Insert child tasks
    # ===========================
    # Only skip parent occurrence, all other valid dates get a task
    for occurrence in occurrences:
        if strip_tz(occurrence) == strip_tz(parent_due_date):
            continue  # parent already created

        child_task_id = await database.execute(
            task.insert().values(
                title=validated.title,
                description=validated.description,
                priority_level=validated.priority_level,
                status=validated.status,
                assigned_to=validated.assigned_to,
                manager_id=validated.manager_id,
                due_date=strip_tz(occurrence),
                related_vendor=validated.related_vendor,
                completion_notes=None,
                completion_date=None,
                project_id=validated.project_id,
                event_id=validated.event_id,
                tenant_id=validated.tenant_id,
                user_group_id=validated.user_group_id,
                event_phase=validated.event_phase,
                recurrence_rule=None,
                recurrence_end_date=None,
                is_main_task=False,
                space_id=validated.space_id,
                asset_id=validated.asset_id,
                is_archived=False,
                archived_at=None,
                created_by=validated.created_by,
                updated_by=validated.created_by,
                created_at=now,
                updated_at=now,
                parent_task_id=parent_task_id
            )
        )

        child_code = generate_code("TASK", child_task_id)
        await database.execute(
            task.update().where(task.c.task_id == child_task_id).values(code=child_code)
        )

    return parent_task

async def list_child_tasks_by_parent(
    tenant_id: int,
    parent_task_id: int,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    page = max(page, 1)
    offset = (page - 1) * page_size

    filters = [
        task.c.tenant_id == tenant_id,
        task.c.parent_task_id == parent_task_id,
    ]

    # Count query
    count_query = select(func.count()).select_from(task).where(and_(*filters))
    total = await database.fetch_val(count_query)

    # Aliases
    assigned_user = aliased(users)
    manager_user = aliased(users)
    vendor_tbl = aliased(vendor)
    project_tbl = aliased(project)
    event_tbl = aliased(event)
    space_tbl = aliased(space)
    asset_tbl = aliased(asset)
    parent_task_tbl = aliased(task)
    user_group_tbl = aliased(user_groups)  # ✅ New alias

    # Select query
    query = (
        select(
            task,
            (assigned_user.c.first_name + ' ' + assigned_user.c.last_name).label("assigned_user_name"),
            (manager_user.c.first_name + ' ' + manager_user.c.last_name).label("manager_user_name"),
            vendor_tbl.c.name.label("vendor_name"),
            project_tbl.c.name.label("project_name"),
            event_tbl.c.title.label("event_title"),
            space_tbl.c.label.label("space_label"),
            asset_tbl.c.name.label("asset_name"),
            parent_task_tbl.c.title.label("parent_task_title"),
            user_group_tbl.c.name.label("user_group_name"),  # ✅ New field
        )
        .select_from(
            task
            .outerjoin(assigned_user, task.c.assigned_to == assigned_user.c.user_id)
            .outerjoin(manager_user, task.c.manager_id == manager_user.c.user_id)
            .outerjoin(vendor_tbl, task.c.related_vendor == vendor_tbl.c.vendor_id)
            .outerjoin(project_tbl, task.c.project_id == project_tbl.c.project_id)
            .outerjoin(event_tbl, task.c.event_id == event_tbl.c.event_id)
            .outerjoin(space_tbl, task.c.space_id == space_tbl.c.space_id)
            .outerjoin(asset_tbl, task.c.asset_id == asset_tbl.c.asset_id)
            .outerjoin(parent_task_tbl, task.c.parent_task_id == parent_task_tbl.c.task_id)
            .outerjoin(user_group_tbl, task.c.user_group_id == user_group_tbl.c.user_group_id)  # ✅ New join
        )
        .where(and_(*filters))
        .order_by(desc(task.c.updated_at))
        .offset(offset)
        .limit(page_size)
    )

    records = await database.fetch_all(query)

    tasks = []
    for r in records:
        task_data = dict(r)
        task_data["assigned_user"] = task_data.pop("assigned_user_name", None)
        task_data["manager_user"] = task_data.pop("manager_user_name", None)
        task_data["vendor_name"] = task_data.pop("vendor_name", None)
        task_data["project_name"] = task_data.pop("project_name", None)
        task_data["event_title"] = task_data.pop("event_title", None)
        task_data["space_label"] = task_data.pop("space_label", None)
        task_data["asset_name"] = task_data.pop("asset_name", None)
        task_data["parent_task_title"] = task_data.pop("parent_task_title", None)
        task_data["user_group_name"] = task_data.pop("user_group_name", None)  # ✅ Add to result
        tasks.append(task_data)

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": tasks
    }
