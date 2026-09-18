# 价格表模型（一个商品可以有多个价格：零售价、批发价、采购价等）

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProductPrice(Base):
    __tablename__ = "product_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # 主键，自增
    # 外键：关联 products 表的 id
    # 相当于告诉数据库"这条价格属于哪个商品"，保证数据不能指向不存在的商品
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    price_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 价格类型：retail 零售 / wholesale 批发 / purchase 采购
    # Numeric(10, 2) 表示总共 10 位数字、其中 2 位小数（适合存金额，避免浮点误差）
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)  # 价格金额
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())  # 创建时间
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )  # 更新时间

    # 关系字段：反向指回所属商品（price.product 可直接拿到商品对象）
    product: Mapped[Product] = relationship(back_populates="prices")