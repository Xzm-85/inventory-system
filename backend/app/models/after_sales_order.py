# 售后单主表 + 售后明细 + 维修记录
# 售后单号自动生成规则：AS + 年月日 + 3位序号，如 AS20260921001
#
# 三种售后类型：
#   return   退货   退序列号/库存回仓
#   exchange 换货   退旧（回仓）+ 发新（出库）
#   repair   维修   只改序列号状态（repairing），不改库存
#
# 所有售后单必须关联原销售订单（original_order_id）。

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AfterSalesOrder(Base):
    __tablename__ = "after_sales_orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # 主键
    # 售后单号，唯一，如 AS20260921001
    after_sales_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    original_order_id: Mapped[int] = mapped_column(
        ForeignKey("sales_orders.id"), nullable=False
    )  # 关联的原销售订单
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)  # 客户
    # 售后类型：return=退货 exchange=换货 repair=维修
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    # 状态：pending=待处理 processing=处理中 completed=已完成 rejected=已拒绝
    status: Mapped[str] = mapped_column(String(20), default="pending")
    reason: Mapped[str | None] = mapped_column(Text)  # 售后原因
    remark: Mapped[str | None] = mapped_column(Text)  # 备注
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # 关系
    original_order: Mapped[SalesOrder] = relationship(back_populates="after_sales_orders")
    customer: Mapped[Customer] = relationship()
    items: Mapped[list[AfterSalesItem]] = relationship(
        back_populates="after_sales", cascade="all, delete-orphan"
    )
    repair_records: Mapped[list[RepairRecord]] = relationship(
        back_populates="after_sales", cascade="all, delete-orphan"
    )


class AfterSalesItem(Base):
    __tablename__ = "after_sales_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # 主键
    after_sales_id: Mapped[int] = mapped_column(
        ForeignKey("after_sales_orders.id"), nullable=False
    )  # 关联售后单
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)  # 商品
    quantity: Mapped[int] = mapped_column(nullable=False)  # 数量
    batch_number: Mapped[str | None] = mapped_column(String(50))  # 退回/原商品批次
    # 退回（或送修）的序列号列表；非序列号商品可空
    serial_numbers: Mapped[list | None] = mapped_column(JSON)
    # 换货时发出的新商品批次（仅 exchange 用）
    new_batch_number: Mapped[str | None] = mapped_column(String(50))
    # 换货时发出的新序列号列表（仅 exchange 的序列号商品用）
    new_serial_numbers: Mapped[list | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # 关系
    after_sales: Mapped[AfterSalesOrder] = relationship(back_populates="items")
    product: Mapped[Product] = relationship()


class RepairRecord(Base):
    __tablename__ = "repair_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # 主键
    after_sales_id: Mapped[int] = mapped_column(
        ForeignKey("after_sales_orders.id"), nullable=False
    )  # 关联售后单（维修类型）
    # 维修状态：received=已收件 inspecting=检测中 repairing=维修中 shipped=已寄回
    status: Mapped[str] = mapped_column(String(20), default="received")
    fault_description: Mapped[str | None] = mapped_column(Text)  # 故障描述
    repair_action: Mapped[str | None] = mapped_column(Text)  # 维修措施
    cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)  # 维修费用
    is_under_warranty: Mapped[bool] = mapped_column(Boolean, default=True)  # 是否在保修期内
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # 关系
    after_sales: Mapped[AfterSalesOrder] = relationship(back_populates="repair_records")