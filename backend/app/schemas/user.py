# 用户表 Schema
# 注意：任何返回给前端的 User 都不包含 password_hash，密码绝不出后端

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str  # 用户名
    password: str  # 明文密码，后端会哈希后存储
    real_name: str | None = None  # 真实姓名
    role_id: int  # 角色
    is_active: bool = True  # 是否启用


class UserUpdate(BaseModel):
    password: str | None = None  # 改密码时传明文，后端自动重新哈希
    real_name: str | None = None
    role_id: int | None = None
    is_active: bool | None = None


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    real_name: str | None
    role_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime