# 角色权限 Schema
# 每条 = 一个角色对某个模块的"四选权限"
# 模块常量：product / purchase / sales / inventory / after_sales / user

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

# 权限模块列表：所有业务模块（后续新增模块往这里加）
PERMISSION_MODULES = [
    "product",      # 商品、单位、分类、价格
    "base_data",    # 供应商、客户、仓库
    "purchase",     # 采购订单、采购入库
    "sales",        # 销售订单、销售出库
    "inventory",    # 库存、序列号查询
    "after_sales",  # 售后单、维修记录
    "payment",      # 收款方式
    "user",         # 用户、角色、权限
]


class RolePermissionItem(BaseModel):
    # 单个模块的权限配置
    module: str = Field(..., pattern="|".join(PERMISSION_MODULES))
    can_view: bool = False  # 查看
    can_create: bool = False  # 新增
    can_edit: bool = False  # 编辑
    can_delete: bool = False  # 删除


class RolePermissionBatch(BaseModel):
    # 批量设置：这次传什么就是什么（整体替换该角色的权限）
    permissions: list[RolePermissionItem]


class RolePermission(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role_id: int
    module: str
    can_view: bool
    can_create: bool
    can_edit: bool
    can_delete: bool
    created_at: datetime