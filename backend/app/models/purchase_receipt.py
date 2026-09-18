# 采购入库单主表 + 明细
# 入库单编号规则：PR + 年月日 + 3位序号，如 PR20260918001

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PurchaseReceipt(Base):
    __tablename__ = "purchase_receipts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # 主键
    receipt_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)  # 入库单号，唯一
    order_id: Mapped[int] = mapped_column(ForeignKey("purchase_orders.id"), nullable=False)  # 关联采购订单
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=False)  # 入库仓库
    remark: Mapped[str | None] = mapped_column(Text)  # 备注
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # 关系
    order: Mapped[PurchaseOrder] = relationship(back_populates="receipts")
    warehouse: Mapped[Warehouse] = relationship()
    items: Mapped[list[PurchaseReceiptItem]] = relationship(
        back_populates="receipt", cascade="all, delete-orphan"
    )


class PurchaseReceiptItem(Base):
    __tablename__ = "purchase_receipt_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # 主键
    receipt_id: Mapped[int] = mapped_column(ForeignKey("purchase_receipts.id"), nullable=False)  # 关联入库单
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)  # 商品
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)  # 入库数量
    batch_number: Mapped[str | None] = mapped_column(String(100))  # 批次号，可选
    # 序列号列表（一台一码时可填），存 JSON 数组
    serial_numbers: Mapped[list | None] = mapped_column(JSON)
    production_date: Mapped[date | None] = mapped_column(Date)  # 生产日期
    expiry_date: Mapped[date | None] = mapped_column(Date)  # 有效期（到期日）
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # 关系
    receipt: Mapped[PurchaseReceipt] = relationship(back_populates="items")
    product: Mapped[Product] = relationship()