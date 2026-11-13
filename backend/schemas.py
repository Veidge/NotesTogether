from pydantic import BaseModel


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