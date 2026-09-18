# 单位表模型（如：台、件、个、盒、箱、套、支）
# 一个 class 对应数据库里一张表，class 的属性对应表的字段

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Unit(Base):
    __tablename__ = "units"  # 数据库中真实表名

    # Mapped[...] 是类型注解：告诉 SQLAlchemy 这个字段是什么类型
    # mapped_column(...) 描述字段的数据库配置
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # 主键，自增
    name: Mapped[str] = mapped_column(String(50), nullable=False)  # 单位名称，必填，最长 50 字符
    # server_default=func.now() ：插入时数据库自动填当前时间
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    # onupdate=func.now() ：每次更新记录时，数据库自动刷新这个时间
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # 关系字段（不生成数据库列）：一个单位可以被多个商品使用
    # 相当于前端的"关联查询"，方便 product.unit 直接拿到单位对象
    products: Mapped[list[Product]] = relationship(back_populates="unit")