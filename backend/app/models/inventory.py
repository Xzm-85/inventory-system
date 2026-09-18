# 库存表
# 一张记录代表一种商品在某仓库中某个批次的数量
# 唯一性维度：商品 + 仓库 + 批次号（批次为空时按空批次处理）

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Inventory(Base):
    __tablename__ = "inventories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # 主键
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)  # 商品
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=False)  # 仓库
    batch_number: Mapped[str | None] = mapped_column(String(100))  # 批次号
    quantity: Mapped[int] = mapped_column(Integer, default=0)  # 库存数量，默认 0
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # 关系
    product: Mapped[Product] = relationship()
    warehouse: Mapped[Warehouse] = relationship()