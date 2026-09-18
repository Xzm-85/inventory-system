# 仓库表模型

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # 主键，自增
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # 仓库名称，必填
    address: Mapped[str | None] = mapped_column(String(500))  # 仓库地址
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())  # 创建时间
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )  # 更新时间