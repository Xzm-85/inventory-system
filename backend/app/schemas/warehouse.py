# 仓库表的 Schema（Create/Update/Read）

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WarehouseBase(BaseModel):
    name: str  # 仓库名称，必填
    address: str | None = None  # 仓库地址


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    name: str | None = None
    address: str | None = None


class Warehouse(WarehouseBase):
    model_config = ConfigDict(from_attributes=True)  # 允许从数据库对象转换

    id: int
    created_at: datetime
    updated_at: datetime