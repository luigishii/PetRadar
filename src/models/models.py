from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    phone: str
    work_phone: Optional[str] = None
    work_email: Optional[EmailStr] = None

class UserResponse(BaseModel):
    id: str
    name: str
    last_name: Optional[str]
    username: str
    email: str
    phone: str
    work_phone: Optional[str]
    work_email: Optional[str]
    status: str
    created_at: str
    
    
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class LoginResponse(BaseModel):
    status: str
    isAdmin: bool
    access_token: str
    token_type: str = "bearer"
    
class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password_hash: Optional[str] = None
    status: Optional[str] = None
    phone: Optional[str] = None
    work_phone: Optional[str] = None
    work_email: Optional[EmailStr] = None
    
    
class CreatePetRequest(BaseModel):
    name: str
    pet_type: str
    size: str
    health_status: str
    breed_name: str  # Alterado de breed_type_id para breed_name
    size_name: Optional[str] = None  # Novo campo para nome do tamanho
    found_at: Optional[datetime] = None