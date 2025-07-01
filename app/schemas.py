from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional
from datetime import datetime

class UserRole(str, Enum):
    ADMIN = "admin"
    HR = "hr"
    MANAGER = "manager"
    EMPLOYEE = "employee"

class RequestType(str, Enum):
    VACATION = "vacation"
    TERMINATION = "termination"
    PAYMENT = "payment"

class RequestStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    department: str
    position: str

class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.EMPLOYEE
    manager_id: Optional[int] = None

class User(UserBase):
    id: int
    is_active: bool
    role: UserRole
    manager_id: Optional[int]

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class RequestBase(BaseModel):
    type: RequestType
    content: str

class RequestCreate(RequestBase):
    pass

class RequestInDB(RequestBase):
    id: int
    status: RequestStatus
    created_at: datetime
    updated_at: datetime
    owner_id: int
    manager_id: int
    hr_officer_id: Optional[int]
    manager_comment: Optional[str]
    hr_comment: Optional[str]
    documents: Optional[str]

    class Config:
        from_attributes = True

class RequestUpdate(BaseModel):
    content: Optional[str]
    status: Optional[RequestStatus]
    manager_comment: Optional[str]
    hr_comment: Optional[str]
    documents: Optional[str]

class TokenData(BaseModel):
    email: Optional[str] = None