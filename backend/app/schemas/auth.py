from pydantic import BaseModel
from typing import Optional, List


class LoginRequest(BaseModel):
    email: str
    password: str



class UserSummary(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_superuser: bool = False
    permissions: List[str] = []


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: UserSummary
