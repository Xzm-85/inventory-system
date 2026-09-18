# 序列号库存表
# 一台一码的商品（enable_serial_tracking=True）入库时，每个序列号单独一行
# 用于后续的销售出库、售后维修等追溯
# status：available 可用 / sold 已售 / repairing 维修中

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SerialInventory(Base):
    __tablename__ = "serial_inventories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # 主键
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)  # 商品
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=False)  # 仓库
    # unique=True：序列号全局唯一，"同一个序列号不能重复入库"由数据库兜底
    serial_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)  # 序列号
    batch_number: Mapped[str | None] = mapped_column(String(100))  # 批次号
    status: Mapped[str] = mapped_column(String(20), default="available", nullable=False)  # 状态
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # 关系
    product: Mapped[Product] = relationship()
    warehouse: Mapped[Warehouse] = relationship()