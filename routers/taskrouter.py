from fastapi import APIRouter, Depends, status, Query
from schemas.taskschema import TaskCreate, TaskUpdate, TaskOut
from schemas.response import StandardResponse
from services import taskservice
from functions.jwt_handler import get_current_user
from schemas.pagination import PaginatedResponse
from typing import Optional, List

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=StandardResponse[TaskOut], status_code=status.HTTP_201_CREATED)
async def create_task(data: TaskCreate):
    task = await taskservice.create_task(data)
    return StandardResponse(isSuccess=True, data=task, message="Task created successfully")

@router.get("/single/{task_id}", response_model=StandardResponse[TaskOut])
async def get_task(task_id: int):
    task = await taskservice.get_task(task_id)
    if task:
        return StandardResponse(isSuccess=True, data=task, message="Task fetched successfully")
    return StandardResponse(isSuccess=False, data=None, message="Task not found")

@router.put("/{task_id}", response_model=StandardResponse[TaskOut])
async def update_task(task_id: int, data: TaskUpdate):
    task = await taskservice.update_task(task_id, data)
    if task:
        return StandardResponse(isSuccess=True, data=task, message="Task updated successfully")
    return StandardResponse(isSuccess=False, data=None, message="Task not found")

@router.delete("/{task_id}", response_model=StandardResponse[dict])
async def delete_task(task_id: int):
    deleted = await taskservice.delete_task(task_id)
    return StandardResponse(isSuccess=True, data={"task_id": task_id}, message="Task deleted successfully")

@router.get("/all", response_model=StandardResponse[list[TaskOut]])
async def all_tasks():
    tasks = await taskservice.all_tasks()
    return StandardResponse(isSuccess=True, data=tasks, message="Tasks fetched successfully")

@router.get("/list-paginated", response_model=StandardResponse[PaginatedResponse[TaskOut]])
async def list_tasks_paginated(
    tenant_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    status: Optional[str] = Query(None),
    priority_level: Optional[str] = Query(None),           # ✅ added
    event_phase: Optional[str] = Query(None),              # ✅ added
    assigned_to: Optional[int] = Query(None),
    manager_id: Optional[int] = Query(None),
    project_id: Optional[int] = Query(None),
    event_id: Optional[int] = Query(None),
    space_id: Optional[int] = Query(None),
    asset_id: Optional[int] = Query(None),
    is_main_task: Optional[str] = Query(None), 
    user_group_id: Optional[int] = Query(None), 
):
    """
    Paginated & filtered task listing.
    """
    tasks = await taskservice.list_tasks_paginated(
        tenant_id=tenant_id,
        page=page,
        page_size=page_size,
        status=status,
        priority_level=priority_level,         # ✅ pass to service
        event_phase=event_phase,               # ✅ pass to service
        assigned_to=assigned_to,
        manager_id=manager_id,
        project_id=project_id,
        event_id=event_id,
        space_id=space_id,
        asset_id=asset_id,
        is_main_task=is_main_task, 
        user_group_id=user_group_id,
    )

    tasks["items"] = [TaskOut(**item) for item in tasks["items"]]

    return StandardResponse(
        isSuccess=True,
        data=PaginatedResponse(**tasks),
        message="Paginated tasks fetched successfully."
    )

@router.get("/tenant/all/{tenant_id}", response_model=StandardResponse[List[TaskOut]])
async def all_tasks_for_tenant(tenant_id: int):
    tasks = await taskservice.get_all_tasks_by_tenant(tenant_id)
    return StandardResponse(isSuccess=True, data=tasks, message="Tasks fetched.")


@router.post("/recurrence", response_model=StandardResponse[TaskOut], status_code=status.HTTP_201_CREATED)
async def create_task_with_recurrence(data: TaskCreate):
    """
    Create a parent task with recurrence, and generate all child tasks according to the recurrence_rule.
    """
    task = await taskservice.create_task_with_recurrence(data)
    return StandardResponse(isSuccess=True, data=task, message="Recurring task(s) created successfully.")


@router.get("/list-child-tasks", response_model=StandardResponse[PaginatedResponse[TaskOut]])
async def list_child_tasks_by_parent(
    tenant_id: int,
    parent_task_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
):
    """
    Fetches paginated list of child tasks for a given parent_task_id.
    Use this to retrieve all tasks generated recursively from a main task.
    """

    tasks = await taskservice.list_child_tasks_by_parent(
        tenant_id=tenant_id,
        parent_task_id= parent_task_id,
        page=page,
        page_size=page_size,
    )

    tasks["items"] = [TaskOut(**item) for item in tasks["items"]]

    return StandardResponse(
        isSuccess=True,
        data=PaginatedResponse(**tasks),
        message="Paginated tasks fetched successfully."
    )
