from datetime import datetime, timedelta
from typing import Optional, Union
from fastapi import HTTPException
from jwt import encode, decode
from app.settings.settings import settings
from app.security.jwttype import JWTType

class JWTManager:
    def __init__(self):
        self.SECRET_KEY = settings.JWT_SECRET_KEY
        self.ALGORITHM = settings.JWT_ALGORITHM
        self.ACCESS_TOKEN_LIFETIME = settings.JWT_ACCESS_TOKEN_LIFETIME_MINUTES
        self.REFRESH_TOKEN_LIFETIME = settings.JWT_REFRESH_TOKEN_LIFETIME_HOURS

    def create_token(self, user_id: int, token_type: JWTType) -> str:
        payload = {
            "UserID": str(user_id),
            "exp": datetime.utcnow() + (timedelta(minutes=self.ACCESS_TOKEN_LIFETIME) if token_type == JWTType.ACCESS else timedelta(hours=self.REFRESH_TOKEN_LIFETIME))
        }
        return encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def decode_token(self, token: str) -> Union[dict, str]:
        try:
            return decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
        except Exception as e:
            return f"Invalid token: {str(e)}"