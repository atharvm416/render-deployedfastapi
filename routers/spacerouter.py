from fastapi import APIRouter, Depends, Query, status
from typing import Optional
from schemas.spaceschema import Space, SpaceCreate, SpaceUpdate
from services import spaceservice
from functions.jwt_handler import get_current_user
from schemas.response import StandardResponse

router = APIRouter(
    prefix="/spaces",
    tags=["Spaces"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=StandardResponse[Space], status_code=status.HTTP_201_CREATED)
async def create_space(data: SpaceCreate):
    space = await spaceservice.create_space(data)
    return StandardResponse(isSuccess=True, data=space, message="Space created successfully.")

@router.get("/", response_model=StandardResponse[dict])
async def list_spaces(
    tenant_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100)
):
    spaces = await spaceservice.get_spaces(tenant_id, page, page_size)
    total = await spaceservice.count_spaces(tenant_id)

    return StandardResponse(
        isSuccess=True,
        data={
            "items": spaces,
            "page": page,
            "page_size": page_size,
            "total": total
        },
        message="Spaces fetched successfully."
    )

@router.put("/{space_id}", response_model=StandardResponse[Space])
async def update_space(space_id: int, data: SpaceUpdate):
    space = await spaceservice.update_space(space_id, data)
    if not space:
        return StandardResponse(isSuccess=False, data=None, message="Space not found.")
    return StandardResponse(isSuccess=True, data=space, message="Space updated successfully.")

@router.delete("/{space_id}", response_model=StandardResponse[dict])
async def delete_space(space_id: int):
    deleted = await spaceservice.delete_space(space_id)
    if deleted:
        return StandardResponse(isSuccess=True, data=None, message="Space deleted successfully.")
    else:
        # still success — it’s already gone
        return StandardResponse(isSuccess=True, data=None, message="Space already deleted or not found.")


@router.get("/all", response_model=StandardResponse[list[dict]])
async def list_all_spaces(tenant_id: int):
    """
    Fetch all spaces for a given tenant_id — no pagination.
    """
    try:
        spaces = await spaceservice.get_all_spaces_for_tenant(tenant_id)

        return StandardResponse(
            isSuccess=True,
            data=spaces,
            message="All spaces fetched successfully."
        )

    except Exception as e:
        return StandardResponse(
            isSuccess=False,
            data=None,
            message=f"Failed to fetch spaces: {str(e)}"
        )

@router.get("/tenant/search/{tenant_id}", response_model=StandardResponse[list[Space]])
async def search_spaces(
    tenant_id: int,
    q: Optional[str] = Query(None, description="Search term for space label (optional)")
):
    results = await spaceservice.search_spaces(query=q, tenant_id=tenant_id)

    return StandardResponse(
        isSuccess=True,
        data=results,
        message=f"Search results for '{q or ''}' in tenant {tenant_id}."
    )
