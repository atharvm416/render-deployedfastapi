from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from schemas.userschema import SignInRequest, User
from schemas.response import StandardResponse
from services import userservice
import json
from functions.jwt_handler import create_access_token

router = APIRouter(tags=["Unauthorized Endpoints"])


@router.post("/signin")
async def signin(data: SignInRequest):
    user = None

    if data.email:
        user = await userservice.authenticate_user_by_email(data.email, data.password)
    elif data.phone:
        user = await userservice.authenticate_user_by_phone(data.phone, data.password)

    if not user:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=json.loads(StandardResponse(
                isSuccess=False,
                data=None,
                message="Invalid email/phone or password."
            ).model_dump_json())
        )

    token = create_access_token({"sub": str(user.user_id)})  # <-- FIXED

    return StandardResponse(
        isSuccess=True,
        data={"access_token": token, "token_type": "bearer", "user_details": user},
        message="User signed in successfully."
    )
