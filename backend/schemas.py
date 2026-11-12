from pydantic import BaseModel


class UserRegister(BaseModel):
    display_name: str
    username: str
    password: str

class UserResponse(BaseModel):
    display_name: str
    username: str