from pydantic import BaseModel, Field
from typing import List, Optional

class UserBase(BaseModel):
    username: str = Field(..., description="用户名")
    roles: List[str] = Field(default=["user"], description="用户角色")
    avatar: Optional[str] = Field(default=None, description="用户头像URL")
    introduction: Optional[str] = Field(default=None, description="用户自我介绍")
    salt: Optional[str] = Field(default=None, description="加密盐")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="密码")

class UserUpdate(BaseModel):
    password: Optional[str] = Field(None, min_length=6, description="新密码")
    roles: Optional[List[str]] = Field(None, description="用户角色")
    avatar: Optional[str] = Field(None, description="用户头像URL")
    introduction: Optional[str] = Field(None, description="用户自我介绍")

class UserOut(UserBase):
    id: int = Field(..., description="用户ID")

    class Config:
        from_attributes = True
