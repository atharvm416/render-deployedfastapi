# routers/event_contact.py
from fastapi import APIRouter, status, Depends
from schemas.eventcontactschema import (
    EventContactCreate,
    EventContactUpdate,
    EventContactOut
)
from schemas.response import StandardResponse
from services import eventcontactservice
from functions.jwt_handler import get_current_user

router = APIRouter(
    prefix="/event-contacts",
    tags=["Event Contacts"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=StandardResponse[EventContactOut], status_code=status.HTTP_201_CREATED)
async def create_event_contact(data: EventContactCreate):
    result = await eventcontactservice.create_event_contact(data)
    return StandardResponse(
        isSuccess=True,
        data=result,
        message="Event contact created successfully."
    )

@router.get("/{contact_id}", response_model=StandardResponse[EventContactOut])
async def get_event_contact(contact_id: int):
    result = await eventcontactservice.get_event_contact(contact_id)
    if not result:
        return StandardResponse(isSuccess=False, data=None, message="Event contact not found.")
    return StandardResponse(isSuccess=True, data=result, message="Event contact fetched successfully.")

@router.put("/{contact_id}", response_model=StandardResponse[EventContactOut])
async def update_event_contact(contact_id: int, data: EventContactUpdate):
    result = await eventcontactservice.update_event_contact(contact_id, data)
    if not result:
        return StandardResponse(isSuccess=False, data=None, message="Event contact not found.")
    return StandardResponse(isSuccess=True, data=result, message="Event contact updated successfully.")

@router.delete("/{contact_id}", response_model=StandardResponse[dict])
async def delete_event_contact(contact_id: int):
    deleted = await eventcontactservice.delete_event_contact(contact_id)
    if not deleted:
        return StandardResponse(isSuccess=False, data=None, message="Event contact not found or already deleted.")
    return StandardResponse(isSuccess=True, data=None, message="Event contact deleted successfully.")

@router.get("/by-event/{event_id}", response_model=StandardResponse[list[EventContactOut]])
async def list_event_contacts(event_id: int):
    contacts = await eventcontactservice.list_event_contacts(event_id)
    contacts = [EventContactOut(**c) for c in contacts]
    return StandardResponse(
        isSuccess=True,
        data=contacts,
        message="Event contacts fetched successfully."
    )
