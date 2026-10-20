from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

class QuestionBase(BaseModel):
    sender_name: Optional[str] = Field(default=None, max_length=40)
    content: str
    images: List[str] = []

class QuestionCreate(QuestionBase):
    content: str = Field(min_length=1, max_length=5000)
    images: List[str] = Field(default_factory=list, max_length=0)

    @field_validator("sender_name")
    @classmethod
    def optional_sender_name(cls, value):
        return value.strip() or None if value is not None else None

    @field_validator("content")
    @classmethod
    def nonblank_content(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("留言不能为空")
        return value

class QuestionOut(QuestionBase):
    id: str
    created_at: datetime
    is_answered: bool
    is_public: bool
    answer_content: Optional[str] = None
    answer_images: List[str] = []
    answered_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AnswerCreate(BaseModel):
    answer_content: str
    answer_images: List[str] = []
    is_public: bool = False

class QuestionUpdate(BaseModel):
    is_public: Optional[bool] = None
    is_answered: Optional[bool] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    question_id: str

class RevokeRequest(BaseModel):
    token: str

# Admin 登录相关
class AdminLogin(BaseModel):
    username: str
    password: str

class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_at: str
