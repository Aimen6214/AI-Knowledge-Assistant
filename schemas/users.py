#Schema (schemas/admin.py) → How data is received from the client and sent back to the client.

from pydantic import BaseModel, EmailStr 
#This tells FastAPI:
#"This class should validate incoming and outgoing data."
#Every Pydantic schema inherits from BaseModel

from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(UserBase): #register user
    password: str  # Add password field for admin creation

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # Allow Pydantic to convert SQLAlchemy model objects into API response objects