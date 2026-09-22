# 角色表
# 预置角色：admin 管理员 / sales 销售 / warehouse 库管 / finance 财务

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # 主键
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # 角色名称，唯一
    description: Mapped[str | None] = mapped_column(Text)  # 角色描述
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # 关系
    users: Mapped[list[User]] = relationship(back_populates="role")
    permissions: Mapped[list[RolePermission]] = relationship(
        back_populates="role", cascade="all, delete-orphan"
    )