from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_session
from app.service.user_service.user_service import UserService
from app.security.jwtmanager import JWTManager
from app.security.hasher import verify_password
from app.models.models import User
from app.security.jwttype import JWTType
from app.schemas.request.users.user_registration_schema import UserRegistration
from app.schemas.request.users.user_update_schema import UserUpdate,UserResponse
from fastapi.security import OAuth2PasswordRequestForm

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

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    login: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    name: Optional[str] = Form(None),
    surname: Optional[str] = Form(None),
    patronymic: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    session: AsyncSession = Depends(get_session)
):
    service = UserService(session)
    
    update_data = {
        "Login": login,
        "Email": email,
        "Name": name,
        "Surname": surname,
        "Patronymic": patronymic,
        "City": city,
        "Phone": phone
    }
    
    update_data = {k: v for k, v in update_data.items() if v is not None}

    try:
        user = await service.update_user_with_photo(user_id, update_data, image)
        return UserResponse(
            UserID=user.UserID,
            Login=user.Login,
            Email=user.Email,
            Name=user.Name,
            Surname=user.Surname,
            Patronymic=user.Patronymic,
            City=user.City,
            Phone=user.Phone,
            PhotoURL=f"http://your-server-domain/uploads/users/{user.PhotoURL.split('/')[-1]}" if user.PhotoURL else None
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обновлении пользователя: {str(e)}"
        )