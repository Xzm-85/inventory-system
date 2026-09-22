# 销售订单主表 + 明细
# 订单编号自动生成规则：SO + 年月日 + 3位序号，如 SO20260918001

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SalesOrder(Base):
    __tablename__ = "sales_orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # 主键
    order_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)  # 订单编号，唯一
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)  # 客户
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=False)  # 发货仓库
    # pending=待出库 partial=部分出库 completed=已完成
    status: Mapped[str] = mapped_column(String(20), default="pending")  # 订单状态
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)  # 订单总金额
    payment_method_id: Mapped[int] = mapped_column(
        ForeignKey("payment_methods.id"), nullable=False
    )  # 收款方式
    # 收款状态：unpaid=未收 partial=部分收款 paid=已收清
    payment_status: Mapped[str] = mapped_column(String(20), default="unpaid")  # 收款状态
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)  # 已收金额
    remark: Mapped[str | None] = mapped_column(Text)  # 备注
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # 关系
    customer: Mapped[Customer] = relationship()
    warehouse: Mapped[Warehouse] = relationship()
    payment_method: Mapped[PaymentMethod] = relationship()
    items: Mapped[list[SalesOrderItem]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    shipments: Mapped[list[SalesShipment]] = relationship(back_populates="order")
    # 预留售后关联：本订单的所有售后记录
    # 通过 after_sales_orders.original_order_id 反向关联（售后表为占位模型，后续补全）
    after_sales_orders: Mapped[list[AfterSalesOrder]] = relationship(
        back_populates="original_order"
    )


class SalesOrderItem(Base):
    __tablename__ = "sales_order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # 主键
    order_id: Mapped[int] = mapped_column(ForeignKey("sales_orders.id"), nullable=False)  # 关联订单
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)  # 商品
    quantity: Mapped[int] = mapped_column(nullable=False)  # 销售数量
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)  # 单价
    # 小计 = 数量 × 单价
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)  # 小计
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # 关系
    order: Mapped[SalesOrder] = relationship(back_populates="items")
    product: Mapped[Product] = relationship()