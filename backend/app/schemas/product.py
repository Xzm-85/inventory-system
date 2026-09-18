# 商品表的 Schema
# 字段和 app/models/product.py 一一对应，但这里负责"对外接口的输入输出格式"

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    name: str  # 商品名称，必填
    specification: str | None = None  # 规格型号
    category_id: int | None = None  # 所属分类 id
    unit_id: int | None = None  # 计量单位 id
    usage: str | None = None  # 商品用途
    image_url: str | None = None  # 商品图片地址
    manufacturer: str | None = None  # 生产厂家
    registration_cert_number: str | None = None  # 医疗器械注册证号
    enable_serial_tracking: bool = False  # 是否启用序列号管理，默认否
    enable_batch_tracking: bool = False  # 是否启用批次管理，默认否
    enable_shelf_life: bool = False  # 是否启用保质期管理，默认否
    shelf_life_days: int | None = None  # 有效期天数
    safety_stock: int | None = None  # 安全库存
    default_supplier_id: int | None = None  # 默认供应商 id
    default_warehouse_id: int | None = None  # 默认仓库 id
    is_medical_device: bool = False  # 是否为医疗器械，默认否
    udi_di: str | None = None  # UDI 产品标识
    extra_attributes: dict | None = None  # 扩展字段，任意 JSON 对象


class ProductCreate(ProductBase):
    pass  # 新增时的请求体（沿用上面全部字段）


# 更新时所有字段都变成可选：只传要改的字段即可（PATCH 式的部分更新）
class ProductUpdate(BaseModel):
    name: str | None = None
    specification: str | None = None
    category_id: int | None = None
    unit_id: int | None = None
    usage: str | None = None
    image_url: str | None = None
    manufacturer: str | None = None
    registration_cert_number: str | None = None
    enable_serial_tracking: bool | None = None
    enable_batch_tracking: bool | None = None
    enable_shelf_life: bool | None = None
    shelf_life_days: int | None = None
    safety_stock: int | None = None
    default_supplier_id: int | None = None
    default_warehouse_id: int | None = None
    is_medical_device: bool | None = None
    udi_di: str | None = None
    extra_attributes: dict | None = None


# 接口返回给前端的结构（含数据库生成的 id、时间）
class Product(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime