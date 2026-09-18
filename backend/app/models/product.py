# 商品表模型：系统的核心表，记录医疗器械商品的基础信息
# 支持序列号/批次/保质期追溯、UDI 追溯等

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # 主键，自增
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # 商品名称，必填
    specification: Mapped[str | None] = mapped_column(String(255))  # 规格型号（| None 表示可空）
    # 外键：关联 categories 表的 id，指向所属分类
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))
    # 外键：关联 units 表的 id，指向计量单位
    unit_id: Mapped[int | None] = mapped_column(ForeignKey("units.id"))
    usage: Mapped[str | None] = mapped_column(String(500))  # 商品用途
    image_url: Mapped[str | None] = mapped_column(String(500))  # 商品图片地址
    manufacturer: Mapped[str | None] = mapped_column(String(255))  # 生产厂家
    registration_cert_number: Mapped[str | None] = mapped_column(String(100))  # 医疗器械注册证号
    # Boolean 对应数据库的布尔值；default=False 表示不传时默认关闭
    enable_serial_tracking: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否启用序列号管理
    enable_batch_tracking: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否启用批次管理
    enable_shelf_life: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否启用保质期管理
    shelf_life_days: Mapped[int | None] = mapped_column(Integer)  # 有效期天数（启用保质期时才填）
    safety_stock: Mapped[int | None] = mapped_column(Integer)  # 安全库存
    # 下述两个字段对应 suppliers / warehouses 表，表尚未建模，先存 int，建表后再补外键
    default_supplier_id: Mapped[int | None] = mapped_column(Integer)  # 默认供应商 id
    default_warehouse_id: Mapped[int | None] = mapped_column(Integer)  # 默认仓库 id
    is_medical_device: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否为医疗器械
    udi_di: Mapped[str | None] = mapped_column(String(255))  # UDI 产品标识
    extra_attributes: Mapped[dict | None] = mapped_column(JSON)  # 扩展字段，存任意 JSON（类似前端的对象）
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())  # 创建时间
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )  # 更新时间

    # 关系字段（不生成列）：
    category: Mapped[Category | None] = relationship(back_populates="products")  # 所属分类对象
    unit: Mapped[Unit | None] = relationship(back_populates="products")  # 计量单位对象
    # 一个商品有多个价格；cascade="all, delete-orphan" 表示删除商品时，连带删除它的价格
    prices: Mapped[list[ProductPrice]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )