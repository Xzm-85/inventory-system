# 角色权限表：一个角色对某个模块的增删改查权限
# 模块：product / purchase / sales / inventory / after_sales / user

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # 主键
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)  # 角色
    module: Mapped[str] = mapped_column(String(50), nullable=False)  # 模块名称
    can_view: Mapped[bool] = mapped_column(Boolean, default=False)  # 查看
    can_create: Mapped[bool] = mapped_column(Boolean, default=False)  # 新增
    can_edit: Mapped[bool] = mapped_column(Boolean, default=False)  # 编辑
    can_delete: Mapped[bool] = mapped_column(Boolean, default=False)  # 删除
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # 关系
    role: Mapped[Role] = relationship(back_populates="permissions")