from fastapi import APIRouter, Query, status, Depends
from schemas.assetsschema import AssetCreate, AssetUpdate, AssetOut
from schemas.response import StandardResponse
from services import assetsservice
from schemas.pagination import PaginatedResponse
from asyncpg.exceptions import UniqueViolationError
from functions.jwt_handler import get_current_user
from typing import Optional

router = APIRouter(
    prefix="/assets",
    tags=["Assets"],
    dependencies=[Depends(get_current_user)]
)


@router.post("/", response_model=StandardResponse[AssetOut], status_code=status.HTTP_201_CREATED)
async def create_asset(data: AssetCreate):
    try:
        result = await assetsservice.create_asset(data)
        return StandardResponse(
            isSuccess=True,
            data=result,
            message="Asset created successfully."
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
            message=f"Failed to create asset: {str(e)}"
        )


@router.get("/{asset_id}", response_model=StandardResponse[AssetOut])
async def get_asset(asset_id: int):
    result = await assetsservice.get_asset(asset_id)
    if not result:
        return StandardResponse(
            isSuccess=False,
            data=None,
            message="Asset not found."
        )
    return StandardResponse(
        isSuccess=True,
        data=result,
        message="Asset fetched successfully."
    )


@router.get("/", response_model=StandardResponse[PaginatedResponse[AssetOut]])
async def list_assets(
    tenant_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: str = Query("all")
):
    try:
        assets = await assetsservice.list_assets_paginated(
            tenant_id=tenant_id, page=page, page_size=page_size, status=status
        )

        assets["items"] = [AssetOut(**item) for item in assets["items"]]

        return StandardResponse(
            isSuccess=True,
            data=PaginatedResponse(**assets),
            message="Assets fetched successfully."
        )

    except Exception as e:
        return StandardResponse(
            isSuccess=False,
            data=None,
            message=f"Failed to fetch assets: {str(e)}"
        )


@router.put("/{asset_id}", response_model=StandardResponse[AssetOut])
async def update_asset(asset_id: int, data: AssetUpdate):
    try:
        updated = await assetsservice.update_asset(asset_id, data)
        if not updated:
            return StandardResponse(
                isSuccess=False,
                data=None,
                message="Asset not found to update."
            )
        return StandardResponse(
            isSuccess=True,
            data=updated,
            message="Asset updated successfully."
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
            message=f"Failed to update asset: {str(e)}"
        )


@router.delete("/{asset_id}", response_model=StandardResponse[dict])
async def delete_asset(asset_id: int):
    try:
        deleted = await assetsservice.delete_asset(asset_id)
        if not deleted:
            return StandardResponse(
                isSuccess=False,
                data=None,
                message="Asset not found or could not be deleted."
            )
        return StandardResponse(
            isSuccess=True,
            data=None,
            message="Asset deleted successfully."
        )
    except Exception as e:
        return StandardResponse(
            isSuccess=False,
            data=None,
            message=f"Failed to delete asset: {str(e)}"
        )

@router.get("/tenant/search/{tenant_id}", response_model=StandardResponse[list[AssetOut]])
async def search_assets(
    tenant_id: int,
    q: Optional[str] = Query(None, description="Search term for asset name (optional)")
):
    results = await assetsservice.search_assets(query=q, tenant_id=tenant_id)

    return StandardResponse(
        isSuccess=True,
        data=results,
        message=f"Search results for '{q or ''}' in tenant {tenant_id}."
    )
