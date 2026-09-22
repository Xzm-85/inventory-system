# 收款方式表
# 预置数据：现金、微信、支付宝、招商银行、对公转账

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # 主键
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # 方式名称，唯一
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # 是否启用
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())