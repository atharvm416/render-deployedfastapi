# routers/project.py
from fastapi import APIRouter, Query, status, Depends
from schemas.projectschema import ProjectCreate, ProjectUpdate, ProjectOut
from schemas.response import StandardResponse
from schemas.pagination import PaginatedResponse
from services import projectservice
from functions.jwt_handler import get_current_user
from asyncpg.exceptions import UniqueViolationError
from typing import Optional

router = APIRouter(
    prefix="/project",
    tags=["Projects"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=StandardResponse[ProjectOut], status_code=status.HTTP_201_CREATED)
async def create_project(data: ProjectCreate):
    try:
        result = await projectservice.create_project(data)
        return StandardResponse(
            isSuccess=True,
            data=result,
            message="Project created successfully."
        )
    except UniqueViolationError:
        return StandardResponse(
            isSuccess=False,
            data=None,
            message="Unique constraint violated."
        )
    except Exception as e:
        return StandardResponse(
            isSuccess=False,
            data=None,
            message=f"Failed to create project: {str(e)}"
        )

@router.get("/{project_id}", response_model=StandardResponse[ProjectOut])
async def get_project(project_id: int):
    result = await projectservice.get_project(project_id)
    if not result:
        return StandardResponse(isSuccess=False, data=None, message="Project not found.")
    return StandardResponse(isSuccess=True, data=result, message="Project fetched successfully.")

@router.put("/{project_id}", response_model=StandardResponse[ProjectOut])
async def update_project(project_id: int, data: ProjectUpdate):
    try:
        result = await projectservice.update_project(project_id, data)
        if not result:
            return StandardResponse(isSuccess=False, data=None, message="Project not found.")
        return StandardResponse(isSuccess=True, data=result, message="Project updated successfully.")
    except Exception as e:
        return StandardResponse(isSuccess=False, data=None, message=f"Failed to update project: {str(e)}")

@router.delete("/{project_id}", response_model=StandardResponse[dict])
async def delete_project(project_id: int):
    deleted = await projectservice.delete_project(project_id)
    return StandardResponse(isSuccess=True, data=None, message="Project deleted successfully.")


@router.get("/", response_model=StandardResponse[PaginatedResponse[ProjectOut]])
async def list_projects(
    tenant_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    project_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None)
):
    try:
        projects = await projectservice.list_projects_paginated(
            tenant_id=tenant_id,
            page=page,
            page_size=page_size,
            project_type=project_type,
            status=status,
            priority=priority
        )

        projects["items"] = [ProjectOut(**item) for item in projects["items"]]

        return StandardResponse(
            isSuccess=True,
            data=PaginatedResponse(**projects),
            message="Projects fetched successfully."
        )

    except Exception as e:
        return StandardResponse(
            isSuccess=False,
            data=None,
            message=f"Failed to fetch projects: {str(e)}"
        )

@router.get("/tenant/search/{tenant_id}", response_model=StandardResponse[list[ProjectOut]])
async def search_projects(
    tenant_id: int,
    q: Optional[str] = Query(None, description="Search term for project name (optional)")
):
    results = await projectservice.search_projects(query=q, tenant_id=tenant_id)

    return StandardResponse(
        isSuccess=True,
        data=results,
        message=f"Search results for '{q or ''}' in tenant {tenant_id}."
    )
