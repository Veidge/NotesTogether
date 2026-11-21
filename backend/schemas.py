from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserRegister(BaseModel):
    display_name: str = Field(min_length=3, max_length=25)
    username: str = Field(min_length=3, max_length=25)
    password: str = Field(min_length=8)

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Некорректное имя: не может состоять из пробелов.")
        return value

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Некорректное имя пользователя: не может состоять из пробелов.")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Некорректный пароль: не может состоять из пробелов.")
        return value

class UserResponse(BaseModel):
    display_name: str
    username: str

class UserLogin(BaseModel):
    username: str = Field(min_length=3, max_length=25)
    password: str = Field(min_length=8)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Некорректное имя пользователя: не может состоять из пробелов.")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Некорректный пароль: не может состоять из пробелов.")
        return value


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    content: str
    color: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Некорректный заголовок: не может состоять из пробелов.")
        return value

class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=50)
    content: str | None = None
    color: str | None = None

    @field_validator("title","content", "color", mode="before")
    @classmethod
    def validate_note_fields(cls, value: str) -> str:
        if value is None:
            raise ValueError("Поля заметки не могут содержать 'null'.")
        return value

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Некорректный заголовок: не может состоять из пробелов.")
        return value

class NoteArchive(BaseModel):
    is_archived: bool

class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    is_owner: bool
    content: str
    color: str
    is_archived: bool
    created_at: datetime
    updated_at: datetime

class TagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    default_tag: bool

class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=25)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Некорректный тег: не может состоять из пробелов.")
        return value

class TagUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=25)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Некорректный тег: не может состоять из пробелов.")
        return value

class UserSharing(BaseModel):
    username: str = Field(min_length=3, max_length=25)
    is_editor: bool

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Некорректное имя пользователя: не может состоять из пробелов.")
        return value

class NoteUserResponse(BaseModel):
    user_id: int
    display_name: str
    username: str
    is_editor: bool

class UserRoleUpdate(BaseModel):
    is_editor: bool