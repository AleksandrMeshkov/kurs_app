from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_session
from app.service.user_service.user_service import UserService
from app.security.jwtmanager import JWTManager
from app.security.hasher import verify_password
from app.models.models import User
from app.security.jwttype import JWTType
from app.schemas.request.users.user_registration_schema import UserRegistration
from app.schemas.request.users.user_update_schema import UserUpdate
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import UploadFile, File
import os
import uuid
from fastapi.responses import JSONResponse


router = APIRouter()

@router.post("/register")
async def register(
    request: UserRegistration,
    session: AsyncSession = Depends(get_session)
):
    user_service = UserService(session)

    existing_user = await user_service.get_user_by_login(request.Login)
    if existing_user:
        raise HTTPException(status_code=400, detail="Login already registered")

    user = await user_service.register(request)
    return {"message": "User created successfully", "user_id": user.UserID}

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    user_service = UserService(session)

    user = await user_service.authenticate_user(form_data.username, form_data.password)
    if isinstance(user, str):
        raise HTTPException(status_code=400, detail=user)

    jwt_manager = JWTManager()
    access_token = jwt_manager.create_token(user.UserID, JWTType.ACCESS)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    user_service = UserService(session)

    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    request: UserUpdate = Depends(),
    photo_file: UploadFile = File(None),
    session: AsyncSession = Depends(get_session)
):
    user_service = UserService(session)
    
    update_data = request.dict(exclude_unset=True)
    
    if photo_file:
        try:
            file_name = await UserService.save_uploaded_file(photo_file)
            # Сохраняем полный URL в базу данных
            full_photo_url = f"http://212.20.53.169:13299/uploads/{file_name}"
            update_data["PhotoURL"] = full_photo_url
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"message": f"Ошибка при загрузке файла: {str(e)}"}
            )
    
    user = await user_service.update_profile(user_id, update_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "message": "User updated successfully",
        "user": user
    }