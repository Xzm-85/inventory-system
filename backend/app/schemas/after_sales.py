# 售后单 Schema
# 三类售后：return 退货 / exchange 换货 / repair 维修
#
# 换货时明细里两组序列号：
#   serial_numbers      退回的商品序列号（sold -> available，库存回仓）
#   new_serial_numbers  发出的新商品序列号（available -> sold，出库）
#   普通商品则用 batch_number / new_batch_number 指定批次

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.repair_record import RepairRecord


# ---- 明细行 ----
class AfterSalesItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)  # 数量，必须大于 0
    batch_number: str | None = None  # 退回/原商品批次
    serial_numbers: list[str] | None = None  # 退回（或送修）序列号
    new_batch_number: str | None = None  # 换货发出的新批次
    new_serial_numbers: list[str] | None = None  # 换货发出的新序列号


class AfterSalesItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    after_sales_id: int
    product_id: int
    quantity: int
    batch_number: str | None
    serial_numbers: list[str] | None
    new_batch_number: str | None
    new_serial_numbers: list[str] | None
    created_at: datetime


# ---- 主表 ----
class AfterSalesCreate(BaseModel):
    original_order_id: int  # 原销售订单，必填，售后不能独立创建
    customer_id: int  # 客户
    type: str  # 售后类型：return / exchange / repair
    reason: str | None = None  # 售后原因
    remark: str | None = None  # 备注
    items: list[AfterSalesItemCreate]  # 至少一条售后明细


class AfterSalesStatusUpdate(BaseModel):
    status: str  # pending / processing / completed / rejected
    remark: str | None = None  # 可一并更新备注


class AfterSales(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    after_sales_number: str
    original_order_id: int
    customer_id: int
    type: str
    status: str
    reason: str | None
    remark: str | None
    created_at: datetime
    updated_at: datetime
    items: list[AfterSalesItem]
    repair_records: list[RepairRecord] | None = Field(default_factory=list)


# 售后类型 / 状态常量
AFTER_SALES_TYPES = ["return", "exchange", "repair"]
AFTER_SALES_STATUSES = ["pending", "processing", "completed", "rejected"]