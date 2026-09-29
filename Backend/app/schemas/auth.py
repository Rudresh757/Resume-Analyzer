from pydantic import BaseModel, EmailStr, Field

class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int | str
    username: str
    email: str

    model_config = {"from_attributes": True}

class AuthSuccessResponse(BaseModel):
    message: str
    user: UserResponse

class MessageResponse(BaseModel):
    message: str
