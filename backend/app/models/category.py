# 商品分类表模型（扁平结构，一维表单，不支持多级分类）

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # 主键，自增
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # 分类名称，必填
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())  # 创建时间，自动生成
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )  # 更新时间，自动刷新

    # 关系字段：一个分类下可以有多个商品
    products: Mapped[list[Product]] = relationship(back_populates="category")