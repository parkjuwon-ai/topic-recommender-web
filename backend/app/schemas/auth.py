from pydantic import BaseModel

from app.schemas.user import UserRead


class GoogleLoginRequest(BaseModel):
    id_token: str


class LoginResponse(BaseModel):
    user: UserRead
    access_token: str
    token_type: str = "bearer"
