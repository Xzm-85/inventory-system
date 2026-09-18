# 商品价格表的 Schema

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductPriceBase(BaseModel):
    product_id: int  # 关联的商品 id，必填
    price_type: str  # 价格类型：retail 零售 / wholesale 批发 / purchase 采购
    price: Decimal  # 价格金额（Decimal 比 float 更精确，适合金额）


class ProductPriceCreate(ProductPriceBase):
    pass  # 新增价格用


# 返回给前端的结构
class ProductPrice(ProductPriceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime