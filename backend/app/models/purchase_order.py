# 采购订单主表
# 订单编号自动生成规则：PO + 年月日 + 3位序号，如 PO20260918001

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # 主键
    order_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)  # 订单编号，唯一
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), nullable=False)  # 供应商
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=False)  # 预计入库仓库
    # pending=待入库 partial=部分入库 completed=已完成
    status: Mapped[str] = mapped_column(String(20), default="pending")  # 订单状态
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)  # 订单总金额
    remark: Mapped[str | None] = mapped_column(Text)  # 备注
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # 关系
    supplier: Mapped[Supplier] = relationship()
    warehouse: Mapped[Warehouse] = relationship()
    items: Mapped[list[PurchaseOrderItem]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    receipts: Mapped[list[PurchaseReceipt]] = relationship(
        back_populates="order"
    )


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # 主键
    order_id: Mapped[int] = mapped_column(ForeignKey("purchase_orders.id"), nullable=False)  # 关联订单
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)  # 商品
    quantity: Mapped[int] = mapped_column(nullable=False)  # 采购数量
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)  # 单价
    # 小计 = 数量 × 单价，入库前由后端计算
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)  # 小计
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # 关系
    order: Mapped[PurchaseOrder] = relationship(back_populates="items")
    product: Mapped[Product] = relationship()