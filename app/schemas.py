from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str
    role:str

class UserResponse(BaseModel):
    id: int           # Unique identifier for the user
    username: str     # The username of the user
    email: str        # The email of the user, if applicable


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to: int
    priority: str
    due_date: datetime
    

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_to:int
    status:str

class TaskStatusUpdate(BaseModel):
    status: str

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    priority: str
    due_date: datetime  # Expecting string format in response
    assigned_to: int  # Expect an integer ID for the assigned user
    status: str

    class Config:
        orm_mode = True
        from_attributes = True 
