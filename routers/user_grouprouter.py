from fastapi import APIRouter, Depends, status, Query
from schemas.usergroupschema import UserGroupCreate, UserGroupUpdate, UserGroup, UserGroupOut
from schemas.response import StandardResponse
from services import user_group_service
from functions.jwt_handler import get_current_user
from asyncpg.exceptions import UniqueViolationError
from typing import Optional
from schemas.pagination import PaginatedResponse

router = APIRouter(
    prefix="/user-groups",
    tags=["User Groups"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=StandardResponse[UserGroup], status_code=status.HTTP_201_CREATED)
async def create_user_group(data: UserGroupCreate):
    try:
        group = await user_group_service.create_user_group(data)
        return StandardResponse(
            isSuccess=True,
            data=group,
            message="User group created successfully."
        )
    except UniqueViolationError as e:
        return StandardResponse(
            isSuccess=False,
            data=None,
            message="Unique constraint violated: " + str(e)
        )
    except Exception as e:
        return StandardResponse(
            isSuccess=False,
            data=None,
            message=f"Unexpected error: {str(e)}"
        )

# @router.get("/{user_group_id}", response_model=StandardResponse[UserGroup])
# async def read_user_group(user_group_id: int):
#     group = await user_group_service.get_user_group(user_group_id)
#     if not group:
#         return StandardResponse(
#             isSuccess=False,
#             data=None,
#             message="User group not found."
#         )
#     return StandardResponse(
#         isSuccess=True,
#         data=group,
#         message="User group fetched successfully."
#     )

@router.get("/", response_model=StandardResponse[list[UserGroup]])
async def read_all_user_groups():
    groups = await user_group_service.get_all_user_groups()
    return StandardResponse(
        isSuccess=True,
        data=groups,
        message="All user groups fetched successfully."
    )

@router.put("/{user_group_id}", response_model=StandardResponse[UserGroup])
async def update_user_group(user_group_id: int, data: UserGroupUpdate):
    try:
        group = await user_group_service.update_user_group(user_group_id, data)
        if not group:
            return StandardResponse(
                isSuccess=False,
                data=None,
                message="User group not found."
            )
        return StandardResponse(
            isSuccess=True,
            data=group,
            message="User group updated successfully."
        )
    except UniqueViolationError as e:
        return StandardResponse(
            isSuccess=False,
            data=None,
            message="Unique constraint violated: " + str(e)
        )
    except Exception as e:
        return StandardResponse(
            isSuccess=False,
            data=None,
            message=f"Unexpected error: {str(e)}"
        )

@router.delete("/{user_group_id}", response_model=StandardResponse[dict])
async def delete_user_group(user_group_id: int):
    deleted = await user_group_service.delete_user_group(user_group_id)
    return StandardResponse(
        isSuccess=True,
        data={"message": "User group deleted successfully."},
        message="User group deleted successfully."
    )

@router.get("/list-paginated", response_model=StandardResponse[PaginatedResponse[UserGroupOut]])
async def get_user_groups_paginated(
    tenant_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    status: Optional[str] = Query(None)
):
    result = await user_group_service.list_user_groups_paginated(
        tenant_id=tenant_id,
        page=page,
        page_size=page_size,
        status=status
    )
    return StandardResponse(
        isSuccess=True,
        data=result,
        message="Paginated user groups fetched successfully."
    )

@router.get("/tenant/search/{tenant_id}", response_model=StandardResponse[list[UserGroupOut]])
async def search_user_groups(
    tenant_id: int,
    q: Optional[str] = Query(None, description="Search term for group name (optional)")
):
    results = await user_group_service.search_user_groups(query=q, tenant_id=tenant_id)

    # Convert each result to match UserGroupOut schema
    group_data = [UserGroupOut(**item) for item in results]

    return StandardResponse(
        isSuccess=True,
        data=group_data,
        message=f"Search results for '{q or ''}' in tenant {tenant_id}."
    )
