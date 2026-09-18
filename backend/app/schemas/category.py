# 分类表的 Schema（扁平结构，只有名称）

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    name: str  # 分类名称，必填


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = None  # 更新时可选


class Category(CategoryBase):
    model_config = ConfigDict(from_attributes=True)  # 允许从数据库对象转换

    id: int
    created_at: datetime
    updated_at: datetime