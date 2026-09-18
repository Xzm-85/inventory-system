# 单位表的 Schema（数据结构定义 + 参数校验）
# 类比前端：Pydantic 的 BaseModel 很像 TypeScript 的 interface，
# 只不过它在"运行时"真正生效，会自动校验和转换前端传来的数据

from datetime import datetime

from pydantic import BaseModel, ConfigDict


# 基础字段：新增和返回都共用的部分
class UnitBase(BaseModel):
    name: str  # 单位名称，必填（没有默认值就是必填）


# 新增时用的结构：请求体长这样
class UnitCreate(UnitBase):
    pass  # 直接继承基础字段，不需要额外字段


# 更新时用的结构：所有字段都是"可选"，因为可能只改其中一部分
class UnitUpdate(BaseModel):
    name: str | None = None  # None 表示可以不传这个字段


# 返回给前端的数据结构（包含数据库生成的字段）
class Unit(UnitBase):
    # from_attributes=True：允许直接把 SQLAlchemy 的模型对象转成这个结构
    # 否则 FastAPI 不知道怎么把"数据库对象"序列化成 JSON
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime