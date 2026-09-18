# 库存 Schema

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