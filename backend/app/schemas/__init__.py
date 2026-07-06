from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    admin = "admin"
    editor = "editor"


class JobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.editor


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# WP Connection schemas
class WPConnectionBase(BaseModel):
    site_name: str
    site_url: HttpUrl
    wp_username: str
    wp_app_password: str


class WPConnectionCreate(WPConnectionBase):
    pass


class WPConnectionResponse(BaseModel):
    id: str
    site_name: str
    site_url: str
    wp_username: str
    created_by: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class WPConnectionTest(BaseModel):
    site_url: HttpUrl
    wp_username: str
    wp_app_password: str


# Import Job schemas
class ImportJobBase(BaseModel):
    source_url: HttpUrl
    target_wp_connection_id: str


class ImportJobCreate(ImportJobBase):
    pass


class ImportJobResponse(BaseModel):
    id: str
    source_url: str
    target_wp_connection_id: str
    status: JobStatus
    wp_post_id: Optional[int] = None
    wp_draft_url: Optional[str] = None
    error_log: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ImportJobBulk(BaseModel):
    urls: list[HttpUrl]
    target_wp_connection_id: str


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
