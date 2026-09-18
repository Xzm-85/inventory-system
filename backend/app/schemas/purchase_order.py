# 采购订单 Schema
# 创建时请求体是"主表 + items 数组"嵌套结构，类似前端的表单子表

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ---- 明细行 ----
class PurchaseOrderItemCreate(BaseModel):
    product_id: int  # 商品
    quantity: int = Field(gt=0)  # 采购数量，必须大于 0
    unit_price: Decimal = Field(gt=0)  # 单价，必须大于 0


class PurchaseOrderItem(PurchaseOrderItemCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    subtotal: Decimal  # 小计（后端计算返回）


# ---- 主表 ----
class PurchaseOrderCreate(BaseModel):
    supplier_id: int  # 供应商，必填
    warehouse_id: int  # 预计入库仓库，必填
    remark: str | None = None  # 备注
    items: list[PurchaseOrderItemCreate]  # 至少一条明细


class PurchaseOrderUpdate(BaseModel):
    status: str | None = None


class PurchaseOrder(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    supplier_id: int
    warehouse_id: int
    status: str
    total_amount: Decimal
    remark: str | None
    created_at: datetime
    updated_at: datetime
    items: list[PurchaseOrderItem]  # 返回时带明细列表