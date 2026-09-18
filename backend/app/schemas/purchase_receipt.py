# 采购入库单 Schema
# 与采购订单一样是"主表 + items 数组"嵌套结构

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ---- 明细行 ----
class PurchaseReceiptItemCreate(BaseModel):
    product_id: int  # 商品
    quantity: int = Field(gt=0)  # 入库数量，必须大于 0
    batch_number: str | None = None  # 批次号
    serial_numbers: list[str] | None = None  # 序列号列表
    production_date: date | None = None  # 生产日期
    expiry_date: date | None = None  # 有效期


class PurchaseReceiptItem(PurchaseReceiptItemCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    receipt_id: int
    created_at: datetime


# ---- 主表 ----
class PurchaseReceiptCreate(BaseModel):
    order_id: int  # 关联采购订单，必填
    warehouse_id: int  # 入库仓库，必填
    remark: str | None = None  # 备注
    items: list[PurchaseReceiptItemCreate]  # 至少一条入库明细


class PurchaseReceipt(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    receipt_number: str
    order_id: int
    warehouse_id: int
    remark: str | None
    created_at: datetime
    items: list[PurchaseReceiptItem]