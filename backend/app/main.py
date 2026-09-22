# 后端入口文件（相当于前端的 main.js / 入口路由）
# 启动命令：uvicorn app.main:app --reload
# 意思是：从 app.main 模块里找到 app 这个服务对象，交给 uvicorn 跑

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, SessionLocal, engine
from app import models  # noqa: F401  确保所有模型注册到 Base.metadata
from app.routers import (
    after_sales,
    auth,
    category,
    customer,
    health,
    inventory,
    payment_method,
    product,
    product_price,
    purchase_order,
    purchase_receipt,
    repair_record,
    role,
    role_permission,
    sales_order,
    sales_shipment,
    supplier,
    unit,
    user,
    warehouse,
)

# 初始数据：单位表预置的 7 个计量单位
UNIT_SEEDS = ["台", "件", "个", "盒", "箱", "套", "支"]
# 初始数据：收款方式表预置的 5 种收款方式
PAYMENT_METHOD_SEEDS = ["现金", "微信", "支付宝", "招商银行", "对公转账"]
# 初始数据：预置角色
ROLE_SEEDS = ["admin", "sales", "warehouse", "finance"]
# 初始数据：内置管理员账号（密码只存哈希）
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


# 应用启动/关闭时的"生命周期钩子"（类似前端的 onMounted / onUnmounted）
# fastapi 在启动时自动调用 create_all 建表，并对单位表做初始化
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. create_all：扫描所有继承 Base 的模型，自动在 MySQL 里建表
    #    （已存在的表不会重复建，只会补建缺失的表）
    Base.metadata.create_all(bind=engine)
    # 2. 初始化单位数据：如果 units 表为空，就预置 7 个单位
    db = SessionLocal()
    try:
        from app.core.security import hash_password
        from app.models import (
            PaymentMethod,
            Role,
            RolePermission,
            Unit,
            User,
        )
        from app.schemas.role_permission import PERMISSION_MODULES

        if db.query(Unit).count() == 0:
            db.add_all([Unit(name=name) for name in UNIT_SEEDS])
            db.commit()
        # 3. 初始化收款方式：如果 payment_methods 表为空，就预置 5 种方式
        if db.query(PaymentMethod).count() == 0:
            db.add_all([PaymentMethod(name=name) for name in PAYMENT_METHOD_SEEDS])
            db.commit()

        # 4. 初始化角色：预置 admin/sales/warehouse/finance
        roles: dict[str, Role] = {}
        for name in ROLE_SEEDS:
            role = db.query(Role).filter(Role.name == name).first()
            if role is None:
                role = Role(name=name)
                db.add(role)
                db.flush()
            roles[name] = role

        # 5. admin 角色默认拥有所有模块的全部权限
        admin_role = roles["admin"]
        existing_permission_modules = {
            p.module for p in admin_role.permissions
        }
        added = False
        for module in PERMISSION_MODULES:
            if module not in existing_permission_modules:
                db.add(
                    RolePermission(
                        role_id=admin_role.id,
                        module=module,
                        can_view=True,
                        can_create=True,
                        can_edit=True,
                        can_delete=True,
                    )
                )
                added = True
        if added:
            db.commit()

        # 6. 初始化内置管理员账号 admin/admin123
        if db.query(User).filter(User.username == ADMIN_USERNAME).first() is None:
            db.add(
                User(
                    username=ADMIN_USERNAME,
                    password_hash=hash_password(ADMIN_PASSWORD),  # 只存哈希
                    real_name="管理员",
                    role_id=admin_role.id,
                    is_active=True,
                )
            )
            db.commit()
    finally:
        db.close()
    yield  # 启动准备完成后，才正式对外提供服务；服务关闭后再执行下面的收尾


# 创建 FastAPI 实例（相当于 new Vue / createApp）
app = FastAPI(title="inventory-system", version="0.1.0", lifespan=lifespan)

# 跨域配置：允许前端（Vue dev server）调用后端接口
# 开发阶段 allow_origins=["*"] 允许所有来源，上线前需要收紧
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册所有路由模块（相当于 Vue Router 里挂 router 配置）
# 每个 router 对象负责一组接口，例如 /units、/categories、/products
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(role.router)
app.include_router(role_permission.router)
app.include_router(unit.router)
app.include_router(category.router)
app.include_router(product.router)
app.include_router(product_price.router)
app.include_router(supplier.router)
app.include_router(customer.router)
app.include_router(warehouse.router)
app.include_router(purchase_order.router)
app.include_router(purchase_receipt.router)
app.include_router(inventory.router)
app.include_router(payment_method.router)
app.include_router(sales_order.router)
app.include_router(sales_shipment.router)
app.include_router(after_sales.router)
app.include_router(after_sales.sales_router)
app.include_router(repair_record.router)
app.include_router(repair_record.records_router)