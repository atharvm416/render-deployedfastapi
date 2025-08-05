# routers/event.py
from fastapi import APIRouter, Query, status, Depends
from typing import Optional
from schemas.eventschema import EventCreate, EventUpdate, EventOut, EventOutWithContacts
from schemas.response import StandardResponse
from schemas.pagination import PaginatedResponse
from services import eventservice
from functions.jwt_handler import get_current_user

router = APIRouter(
    prefix="/events",
    tags=["Events"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=StandardResponse[EventOut], status_code=status.HTTP_201_CREATED)
async def create_event(data: EventCreate):
    result = await eventservice.create_event(data)
    return StandardResponse(
        isSuccess=True,
        data=result,
        message="Event created successfully."
    )

@router.get("/{event_id}", response_model=StandardResponse[EventOut])
async def get_event(event_id: int):
    result = await eventservice.get_event(event_id)
    if not result:
        return StandardResponse(isSuccess=False, data=None, message="Event not found.")
    return StandardResponse(isSuccess=True, data=result, message="Event fetched successfully.")

@router.put("/{event_id}", response_model=StandardResponse[EventOut])
async def update_event(event_id: int, data: EventUpdate):
    result = await eventservice.update_event(event_id, data)
    if not result:
        return StandardResponse(isSuccess=False, data=None, message="Event not found.")
    return StandardResponse(isSuccess=True, data=result, message="Event updated successfully.")

@router.delete("/{event_id}", response_model=StandardResponse[dict])
async def delete_event(event_id: int):
    deleted = await eventservice.delete_event(event_id)
    return StandardResponse(isSuccess=True, data=None, message="Event deleted successfully.")

@router.get("/", response_model=StandardResponse[PaginatedResponse[EventOutWithContacts]])
async def list_events(
    tenant_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    status: Optional[str] = Query(None)
):
    events = await eventservice.list_events_paginated(
        tenant_id=tenant_id,
        page=page,
        page_size=page_size,
        status=status
    )

    events["items"] = [EventOutWithContacts(**item) for item in events["items"]]

    return StandardResponse(
        isSuccess=True,
        data=PaginatedResponse(**events),
        message="Events fetched successfully."
    )

@router.get("/tenant/search/{tenant_id}", response_model=StandardResponse[list[EventOut]])
async def search_events(
    tenant_id: int,
    q: Optional[str] = Query(None, description="Search term for event title (optional)")
):
    results = await eventservice.search_events(query=q, tenant_id=tenant_id)

    return StandardResponse(
        isSuccess=True,
        data=results,
        message=f"Search results for '{q or ''}' in tenant {tenant_id}."
    )
