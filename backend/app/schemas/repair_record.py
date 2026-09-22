# 维修记录 Schema
# 维修单节点：received 已收件 / inspecting 检测中 / repairing 维修中 / shipped 已寄回

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class RepairRecordCreate(BaseModel):
    status: str = "received"  # 初始状态：已收件
    fault_description: str | None = None  # 故障描述
    repair_action: str | None = None  # 维修措施
    cost: Decimal | None = None  # 维修费用
    is_under_warranty: bool = True  # 是否在保修期内


class RepairRecordUpdate(BaseModel):
    status: str | None = None
    fault_description: str | None = None
    repair_action: str | None = None
    cost: Decimal | None = None
    is_under_warranty: bool | None = None


class RepairRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    after_sales_id: int
    status: str
    fault_description: str | None
    repair_action: str | None
    cost: Decimal
    is_under_warranty: bool
    created_at: datetime
    updated_at: datetime


REPAIR_STATUSES = ["received", "inspecting", "repairing", "shipped"]