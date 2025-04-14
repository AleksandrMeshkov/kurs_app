from pydantic import BaseModel

class UserAuth(BaseModel):
    Login: str
    Password: str