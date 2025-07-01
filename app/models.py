from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
from enum import Enum


# Определяем enum для типов ролей пользователей
class UserRole(str, Enum):
    ADMIN = "admin"
    HR = "hr"
    MANAGER = "manager"
    EMPLOYEE = "employee"


# Определяем enum для типов запросов
class RequestType(str, Enum):
    VACATION = "vacation"
    TERMINATION = "termination"
    PAYMENT = "payment"


# Определяем enum для статусов запросов
class RequestStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    department = Column(String)
    position = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(SQLEnum(UserRole), default=UserRole.EMPLOYEE)  # Используем SQLEnum
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    requests = relationship("Request", back_populates="owner")
    managed_requests = relationship("Request", back_populates="manager")
    hr_requests = relationship("Request", back_populates="hr_officer")
    subordinates = relationship("User", remote_side=[id])


class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(SQLEnum(RequestType))  # Используем SQLEnum
    status = Column(SQLEnum(RequestStatus), default=RequestStatus.DRAFT)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    content = Column(Text)
    documents = Column(Text, nullable=True)
    manager_comment = Column(Text, nullable=True)
    hr_comment = Column(Text, nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id"))
    manager_id = Column(Integer, ForeignKey("users.id"))
    hr_officer_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    owner = relationship("User", foreign_keys=[owner_id], back_populates="requests")
    manager = relationship("User", foreign_keys=[manager_id], back_populates="managed_requests")
    hr_officer = relationship("User", foreign_keys=[hr_officer_id], back_populates="hr_requests")