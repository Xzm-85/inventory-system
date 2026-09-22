# 用户表
# 密码只存 bcrypt 哈希值（password_hash），绝不存明文

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # 主键
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # 用户名，唯一
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)  # 密码哈希值
    real_name: Mapped[str | None] = mapped_column(String(50))  # 真实姓名
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)  # 角色
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # 是否启用
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # 关系
    role: Mapped[Role] = relationship(back_populates="users")