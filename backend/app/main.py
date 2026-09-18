# 后端入口文件（相当于前端的 main.js / 入口路由）
# 启动命令：uvicorn app.main:app --reload
# 意思是：从 app.main 模块里找到 app 这个服务对象，交给 uvicorn 跑

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, SessionLocal, engine
from app import models  # noqa: F401  确保所有模型注册到 Base.metadata
from app.routers import (
    category,
    customer,
    health,
    inventory,
    product,
    product_price,
    purchase_order,
    purchase_receipt,
    supplier,
    unit,
    warehouse,
)

# 初始数据：单位表预置的 7 个计量单位
UNIT_SEEDS = ["台", "件", "个", "盒", "箱", "套", "支"]


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
        from app.models import Unit

        if db.query(Unit).count() == 0:
            db.add_all([Unit(name=name) for name in UNIT_SEEDS])
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