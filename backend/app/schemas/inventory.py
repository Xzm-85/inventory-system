# 库存 Schema（含序列号库存相关）

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Inventory(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    warehouse_id: int
    batch_number: str | None
    quantity: int
    created_at: datetime
    updated_at: datetime


# 单条可用序列号信息（对应 SerialInventory 表）
class SerialInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    serial_number: str
    batch_number: str | None
    status: str


# GET /inventories/serials 的返回结构
class AvailableSerialsResponse(BaseModel):
    product_id: int
    warehouse_id: int
    serials: list[SerialInfo]