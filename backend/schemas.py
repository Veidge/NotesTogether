from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UserRegister(BaseModel):
    display_name: str
    username: str
    password: str

class UserResponse(BaseModel):
    display_name: str
    username: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class NoteCreate(BaseModel):
    title: str
    content: str
    color: str

class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    color: str | None = None
    is_archived: bool | None = None

class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    color: str
    is_archived: bool
    created_at: datetime
    updated_at: datetime