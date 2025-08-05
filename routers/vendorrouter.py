from fastapi import APIRouter, Query, status, Depends
from schemas.vendorschema import VendorCreate, VendorUpdate, VendorOut
from schemas.response import StandardResponse
from schemas.pagination import PaginatedResponse
from services import vendorservice
from asyncpg.exceptions import UniqueViolationError
from functions.jwt_handler import get_current_user
from typing import Optional, List

router = APIRouter(
    prefix="/vendor",
    tags=["Vendor"],
    dependencies=[Depends(get_current_user)]
)


@router.post("/", response_model=StandardResponse[VendorOut], status_code=status.HTTP_201_CREATED)
async def create_vendor(data: VendorCreate):
    try:
        result = await vendorservice.create_vendor(data)
        return StandardResponse(
            isSuccess=True,
            data=result,
            message="Vendor created successfully."
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
            message=f"Failed to create vendor: {str(e)}"
        )


@router.get("/{vendor_id}", response_model=StandardResponse[VendorOut])
async def get_vendor(vendor_id: int):
    result = await vendorservice.get_vendor(vendor_id)
    if not result:
        return StandardResponse(
            isSuccess=False,
            data=None,
            message="Vendor not found."
        )
    return StandardResponse(
        isSuccess=True,
        data=result,
        message="Vendor fetched successfully."
    )


@router.get("/", response_model=StandardResponse[PaginatedResponse[VendorOut]])
async def list_vendors(
    tenant_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: str = Query("all"),
    vendor_type: Optional[str] = None,
    compliance_status: Optional[str] = None,
    payment_terms: Optional[str] = None
):
    try:
        vendors = await vendorservice.list_vendors_paginated(
            tenant_id=tenant_id,
            page=page,
            page_size=page_size,
            status=status,
            vendor_type=vendor_type,
            compliance_status=compliance_status,
            payment_terms=payment_terms
        )

        vendors["items"] = [VendorOut(**item) for item in vendors["items"]]

        return StandardResponse(
            isSuccess=True,
            data=PaginatedResponse(**vendors),
            message="Vendors fetched successfully."
        )

    except Exception as e:
        return StandardResponse(
            isSuccess=False,
            data=None,
            message=f"Failed to fetch vendors: {str(e)}"
        )


@router.put("/{vendor_id}", response_model=StandardResponse[VendorOut])
async def update_vendor(vendor_id: int, data: VendorUpdate):
    try:
        updated = await vendorservice.update_vendor(vendor_id, data)
        if not updated:
            return StandardResponse(
                isSuccess=False,
                data=None,
                message="Vendor not found to update."
            )
        return StandardResponse(
            isSuccess=True,
            data=updated,
            message="Vendor updated successfully."
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
            message=f"Failed to update vendor: {str(e)}"
        )


@router.delete("/{vendor_id}", response_model=StandardResponse[dict])
async def delete_vendor(vendor_id: int):
    try:
        deleted = await vendorservice.delete_vendor(vendor_id)
        if not deleted:
            return StandardResponse(
                isSuccess=False,
                data=None,
                message="Vendor not found or could not be deleted."
            )
        return StandardResponse(
            isSuccess=True,
            data=None,
            message="Vendor deleted successfully."
        )
    except Exception as e:
        return StandardResponse(
            isSuccess=False,
            data=None,
            message=f"Failed to delete vendor: {str(e)}"
        )

@router.get("/tenant/search/{tenant_id}", response_model=StandardResponse[list[VendorOut]])
async def search_vendors(
    tenant_id: int,
    q: Optional[str] = Query(None, description="Search term for vendor name (optional)")
):
    results = await vendorservice.search_vendors(query=q, tenant_id=tenant_id)

    return StandardResponse(
        isSuccess=True,
        data=results,
        message=f"Search results for '{q or ''}' in tenant {tenant_id}."
    )
