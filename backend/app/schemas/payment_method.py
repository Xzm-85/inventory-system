# 收款方式表的 Schema（Create/Update/Read）

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PaymentMethodCreate(BaseModel):
    name: str  # 方式名称，必填
    is_active: bool = True  # 是否启用，默认 True


class PaymentMethodUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None


class PaymentMethod(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    is_active: bool
    created_at: datetime