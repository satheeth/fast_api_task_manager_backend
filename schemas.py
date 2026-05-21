from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenRefresh(BaseModel):
    refresh_token: str

class TaskBase(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None

class TaskResponse(TaskBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)