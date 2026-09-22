# 销售出库单 Schema

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ---- 明细行 ----
class SalesShipmentItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)  # 出库数量，必须大于 0
    batch_number: str | None = None  # 批次号，可选
    serial_numbers: list[str] | None = None  # 序列号列表，序列号管理商品必填


class SalesShipmentItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    shipment_id: int
    product_id: int
    quantity: int
    batch_number: str | None
    serial_numbers: list[str] | None
    created_at: datetime


# ---- 主表 ----
class SalesShipmentCreate(BaseModel):
    order_id: int  # 销售订单，必填
    warehouse_id: int  # 出库仓库，必填
    remark: str | None = None  # 备注
    items: list[SalesShipmentItemCreate]  # 至少一条出库明细


class SalesShipment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    shipment_number: str
    order_id: int
    warehouse_id: int
    remark: str | None
    created_at: datetime
    items: list[SalesShipmentItem]