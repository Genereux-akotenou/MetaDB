from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from .models import UserRole, QAStatus


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str | None = ""
    password: str = Field(min_length=6)
    role: UserRole


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True


class ChunkIn(BaseModel):
    chunk_id: str
    source_url: str | None = ""
    content: str


class ChunkOut(ChunkIn):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class QAIn(BaseModel):
    chunk_id: int
    question: str
    answer: str
    category_id: Optional[int] = None


class QAOut(BaseModel):
    id: int
    chunk_id: int
    question: str
    answer: str
    category_id: Optional[int] = None
    status: QAStatus
    created_at: datetime

    class Config:
        from_attributes = True


class AnnotationIn(BaseModel):
    qa_item_id: int
    edited_question: str
    edited_answer: str
    score: float = 0.0
    comment: str = ""
    validated: bool = False


class AnnotationOut(BaseModel):
    id: int
    qa_item_id: int
    edited_question: str
    edited_answer: str
    score: float
    comment: str
    validated: bool
    created_at: datetime

    class Config:
        from_attributes = True


