# 客户表的 Schema（Create/Update/Read）

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class CustomerBase(BaseModel):
    name: str  # 客户名称，必填
    contact_person: str | None = None  # 联系人
    phone: str | None = None  # 电话
    address: str | None = None  # 地址
    license_number: str | None = None  # 营业执照号
    medical_device_license: str | None = None  # 医疗器械经营许可证号
    license_expiry_date: date | None = None  # 证照有效期


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: str | None = None
    contact_person: str | None = None
    phone: str | None = None
    address: str | None = None
    license_number: str | None = None
    medical_device_license: str | None = None
    license_expiry_date: date | None = None


class Customer(CustomerBase):
    model_config = ConfigDict(from_attributes=True)  # 允许从数据库对象转换

    id: int
    created_at: datetime
    updated_at: datetime