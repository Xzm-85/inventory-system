# 销售订单 Schema
# 与采购订单一样是"主表 + items 数组"嵌套结构

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ---- 明细行 ----
class SalesOrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)  # 销售数量，必须大于 0
    unit_price: Decimal = Field(gt=0)  # 单价


class SalesOrderItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    created_at: datetime


# ---- 主表 ----
class SalesOrderCreate(BaseModel):
    customer_id: int  # 客户，必填
    warehouse_id: int  # 发货仓库，必填
    payment_method_id: int  # 收款方式，必填
    remark: str | None = None  # 备注
    items: list[SalesOrderItemCreate]  # 至少一条销售明细


class SalesOrder(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    customer_id: int
    warehouse_id: int
    status: str
    total_amount: Decimal
    payment_method_id: int
    payment_status: str
    paid_amount: Decimal
    remark: str | None
    created_at: datetime
    updated_at: datetime
    items: list[SalesOrderItem]