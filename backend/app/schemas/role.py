# 角色表 Schema

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RoleCreate(BaseModel):
    name: str  # 角色名称，唯一（如 admin / sales / warehouse / finance）
    description: str | None = None  # 角色描述


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class Role(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime