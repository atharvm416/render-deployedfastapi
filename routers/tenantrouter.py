from fastapi import APIRouter, Query, status, Depends
from schemas.tenantschema import TenantCreate, TenantUpdate, Tenant
from schemas.response import StandardResponse
from services import tenantservice
from schemas.pagination import PaginatedResponse
from asyncpg.exceptions import UniqueViolationError
from functions.jwt_handler import get_current_user
from typing import Optional

router = APIRouter(
    prefix="/tenants",
    tags=["Tenants"],
    dependencies=[Depends(get_current_user)]
)


@router.post("/", response_model=StandardResponse[Tenant], status_code=status.HTTP_201_CREATED)
async def create_tenant(data: TenantCreate):
    try:
        result = await tenantservice.create_tenant(data)
        return StandardResponse(
            isSuccess=True,
            data=result,
            message="Tenant created successfully."
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
            message=f"Failed to create tenant: {str(e)}"
        )


@router.get("/{tenant_id}", response_model=StandardResponse[Tenant])
async def get_tenant(tenant_id: int):
    result = await tenantservice.get_tenant(tenant_id)
    if not result:
        return StandardResponse(
            isSuccess=False,
            data=None,
            message="Tenant not found."
        )
    return StandardResponse(
        isSuccess=True,
        data=result,
        message="Tenant fetched successfully."
    )


@router.get("/", response_model=StandardResponse[PaginatedResponse[Tenant]])
async def list_tenants(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    try:
        tenants = await tenantservice.list_tenants_paginated(page=page, page_size=page_size)

        tenants["items"] = [Tenant(**item) for item in tenants["items"]]

        return StandardResponse(
            isSuccess=True,
            data=PaginatedResponse(**tenants),
            message="Tenants fetched successfully."
        )

    except Exception as e:
        return StandardResponse(
            isSuccess=False,
            data=None,
            message=f"Failed to fetch tenants: {str(e)}"
        )


@router.put("/{tenant_id}", response_model=StandardResponse[Tenant])
async def update_tenant(tenant_id: int, data: TenantUpdate):
    try:
        updated = await tenantservice.update_tenant(tenant_id, data)
        if not updated:
            return StandardResponse(
                isSuccess=False,
                data=None,
                message="Tenant not found to update."
            )
        return StandardResponse(
            isSuccess=True,
            data=updated,
            message="Tenant updated successfully."
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
            message=f"Failed to update tenant: {str(e)}"
        )


@router.delete("/{tenant_id}", response_model=StandardResponse[dict])
async def delete_tenant(tenant_id: int):
    try:
        deleted = await tenantservice.delete_tenant(tenant_id)
        if not deleted:
            return StandardResponse(
                isSuccess=False,
                data={"tenant_id": tenant_id},
                message="Tenant not found or could not be deleted."
            )
        return StandardResponse(
            isSuccess=True,
            data={"tenant_id": tenant_id},
            message="Tenant deleted successfully."
        )
    except Exception as e:
        return StandardResponse(
            isSuccess=False,
            data={"tenant_id": tenant_id},
            message=f"Failed to delete tenant: {str(e)}"
        )
    
@router.get("/alltenant/fetch", response_model=StandardResponse[list[Tenant]])
async def read_all_tenants():
    tenants = await tenantservice.get_all_tenants()
    return StandardResponse(
        isSuccess=True,
        data=tenants,
        message="All tenants fetched successfully."
    )

@router.get("/tenant/search", response_model=StandardResponse[list[Tenant]])
async def search_tenant(
    q: Optional[str] = Query(None, description="Search by name, code, or contact name")
):
    results = await tenantservice.search_tenants(query=q)

    return StandardResponse(
        isSuccess=True,
        data=results,
        message=f"Search results for '{q or ''}'"
    )