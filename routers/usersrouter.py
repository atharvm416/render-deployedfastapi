from fastapi import APIRouter, Depends, status, Query
from schemas.userschema import UserCreate, UserUpdate, User, PasswordUpdateRequest
from schemas.response import StandardResponse
from services import userservice
from asyncpg.exceptions import UniqueViolationError
from functions.jwt_handler import get_current_user
from typing import Optional

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(get_current_user)]
)


@router.post("/", response_model=StandardResponse[User], status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate):
    try:
        user = await userservice.create_user(data)
        return StandardResponse(
            isSuccess=True,
            data=user,
            message="User created successfully."
        )
    except UniqueViolationError as e:
        msg = "Unique constraint violated."
        if 'users_phone_key' in str(e):
            msg = "Phone number already exists."
        elif 'users_email_key' in str(e):
            msg = "Email already exists."
        return StandardResponse(
            isSuccess=False,
            data=None,
            message=msg
        )
    except Exception as e:
        return StandardResponse(
            isSuccess=False,
            data=None,
            message=f"Unexpected error: {str(e)}"
        )


@router.get("/{user_id}", response_model=StandardResponse[User])
async def read_user(user_id: int):
    user = await userservice.get_user(user_id)
    if not user:
        return StandardResponse(
            isSuccess=False,
            data=None,
            message="User not found."
        )
    return StandardResponse(
        isSuccess=True,
        data=user,
        message="User fetched successfully."
    )


@router.get("/", response_model=StandardResponse[list[User]])
async def read_all_users():
    users = await userservice.get_all_users()
    return StandardResponse(
        isSuccess=True,
        data=users,
        message="All users fetched successfully."
    )


@router.put("/{user_id}", response_model=StandardResponse[User])
async def update_user(user_id: int, data: UserUpdate):
    try:
        user = await userservice.update_user(user_id, data)
        if not user:
            return StandardResponse(
                isSuccess=False,
                data=None,
                message="User not found."
            )
        return StandardResponse(
            isSuccess=True,
            data=user,
            message="User updated successfully."
        )
    except UniqueViolationError as e:
        msg = "Unique constraint violated."
        if 'users_phone_key' in str(e):
            msg = "Phone number already exists."
        elif 'users_email_key' in str(e):
            msg = "Email already exists."
        return StandardResponse(
            isSuccess=False,
            data=None,
            message=msg
        )
    except Exception as e:
        return StandardResponse(
            isSuccess=False,
            data=None,
            message=f"Unexpected error: {str(e)}"
        )


@router.delete("/{user_id}", response_model=StandardResponse[dict])
async def delete_user(user_id: int):
    deleted = await userservice.delete_user(user_id)
    return StandardResponse(
        isSuccess=True,
        data={"message": "User deleted successfully."},
        message="User deleted successfully."
    )

@router.post("/{user_id}/update-password", response_model=StandardResponse[dict])
async def update_password(user_id: int, payload: PasswordUpdateRequest):
    try:
        success = await userservice.update_password(user_id, payload.new_password)
        if not success:
            return StandardResponse(
                isSuccess=False,
                data=None,
                message="User not found."
            )
        return StandardResponse(
            isSuccess=True,
            data={},
            message="Password updated successfully."
        )
    except Exception as e:
        return StandardResponse(
            isSuccess=False,
            data=None,
            message=f"Unexpected error: {str(e)}"
        )

@router.get("/tenant/{tenant_id}/paginated", response_model=StandardResponse[dict])
async def get_users_paginated(
    tenant_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    role: str = Query(None)
):
    """
    Get users by tenant_id (paginated), optionally filter by role.
    """
    result = await userservice.list_users_paginated(
        tenant_id=tenant_id,
        page=page,
        page_size=page_size,
        role=role
    )

    return StandardResponse(
        isSuccess=True,
        data=result,
        message="Paginated users fetched successfully."
    )

@router.get("/role/{role}", response_model=StandardResponse[list[User]])
async def get_users_by_role(role: str):
    """
    Get all users by role (no pagination).
    """
    users = await userservice.list_users_by_role(role)

    return StandardResponse(
        isSuccess=True,
        data=users,
        message=f"All users with role '{role}' fetched successfully."
    )

@router.get("/tenant/search/{tenant_id}", response_model=StandardResponse[list[User]])
async def search_users(
    tenant_id: int,
    q: Optional[str] = Query(None, description="Search term for first/last name (optional)")
):
    results = await userservice.search_users(query=q, tenant_id=tenant_id)

    return StandardResponse(
        isSuccess=True,
        data=results,
        message=f"Search results for '{q or ''}' in tenant {tenant_id}."
    )

