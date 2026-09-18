# 客户表模型：记录医疗器械客户及其证照信息

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # 主键，自增
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # 客户名称，必填
    contact_person: Mapped[str | None] = mapped_column(String(50))  # 联系人
    phone: Mapped[str | None] = mapped_column(String(50))  # 电话
    address: Mapped[str | None] = mapped_column(String(500))  # 地址
    license_number: Mapped[str | None] = mapped_column(String(100))  # 营业执照号
    medical_device_license: Mapped[str | None] = mapped_column(String(100))  # 医疗器械经营许可证号
    license_expiry_date: Mapped[date | None] = mapped_column(Date)  # 证照有效期
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())  # 创建时间
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )  # 更新时间