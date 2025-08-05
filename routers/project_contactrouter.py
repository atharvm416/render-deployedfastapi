# routers/project_contact.py
from fastapi import APIRouter, status, Depends
from schemas.project_contactschema import (
    ProjectContactCreate, ProjectContactUpdate, ProjectContactOut
)
from schemas.response import StandardResponse
from services import project_contactservice
from functions.jwt_handler import get_current_user

router = APIRouter(
    prefix="/project-contacts",
    tags=["Project Contacts"],
        dependencies=[Depends(get_current_user)]

)

@router.post("/", response_model=StandardResponse[ProjectContactOut], status_code=status.HTTP_201_CREATED)
async def create_project_contact(data: ProjectContactCreate):
    contact = await project_contactservice.create_contact(data)
    return StandardResponse(
        isSuccess=True,
        data=contact,
        message="Contact created successfully."
    )

@router.get("/{contact_id}", response_model=StandardResponse[ProjectContactOut])
async def get_project_contact(contact_id: int):
    contact = await project_contactservice.get_contact(contact_id)
    if not contact:
        return StandardResponse(isSuccess=False, data=None, message="Contact not found.")
    return StandardResponse(isSuccess=True, data=contact, message="Contact fetched successfully.")

@router.put("/{contact_id}", response_model=StandardResponse[ProjectContactOut])
async def update_project_contact(contact_id: int, data: ProjectContactUpdate):
    contact = await project_contactservice.update_contact(contact_id, data)
    if not contact:
        return StandardResponse(isSuccess=False, data=None, message="Contact not found.")
    return StandardResponse(isSuccess=True, data=contact, message="Contact updated successfully.")

@router.delete("/{contact_id}", response_model=StandardResponse[dict])
async def delete_project_contact(contact_id: int):
    deleted = await project_contactservice.delete_contact(contact_id)
    if not deleted:
        return StandardResponse(isSuccess=False, data=None, message="Contact not found or already deleted.")
    return StandardResponse(isSuccess=True, data=None, message="Contact deleted successfully.")
