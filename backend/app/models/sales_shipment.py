# 销售出库单主表 + 明细
# 出库单号自动生成规则：SS + 年月日 + 3位序号，如 SS20260918001

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SalesShipment(Base):
    __tablename__ = "sales_shipments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # 主键
    shipment_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)  # 出库单号，唯一
    order_id: Mapped[int] = mapped_column(ForeignKey("sales_orders.id"), nullable=False)  # 关联销售订单
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=False)  # 出库仓库
    remark: Mapped[str | None] = mapped_column(Text)  # 备注
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # 关系
    order: Mapped[SalesOrder] = relationship(back_populates="shipments")
    warehouse: Mapped[Warehouse] = relationship()
    items: Mapped[list[SalesShipmentItem]] = relationship(
        back_populates="shipment", cascade="all, delete-orphan"
    )


class SalesShipmentItem(Base):
    __tablename__ = "sales_shipment_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # 主键
    shipment_id: Mapped[int] = mapped_column(
        ForeignKey("sales_shipments.id"), nullable=False
    )  # 关联出库单
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)  # 商品
    quantity: Mapped[int] = mapped_column(nullable=False)  # 出库数量
    batch_number: Mapped[str | None] = mapped_column(String(50))  # 批次号，可选
    serial_numbers: Mapped[list | None] = mapped_column(JSON)  # 序列号列表，序列号管理商品专用
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # 关系
    shipment: Mapped[SalesShipment] = relationship(back_populates="items")
    product: Mapped[Product] = relationship()