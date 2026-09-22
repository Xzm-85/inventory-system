# 售后接口
#   POST /after-sales                    创建售后单（强制关联原订单）
#   GET  /after-sales?order_id=          列表（可按订单过滤）
#   GET  /after-sales/{id}               详情
#   PUT  /after-sales/{id}               状态更新（pending/processing/completed/rejected）
#   GET  /sales-orders/{id}/after-sales  某个销售订单的所有售后单

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.deps import require_permission
from sqlalchemy.orm import Session

from app.crud.after_sales import (
    create_after_sales,
    get_after_sales,
    get_after_sales_list,
    update_after_sales_status,
)
from app.crud.customer import get_customer
from app.crud.inventory import get_inventory_by_key, get_serial_by_number
from app.crud.product import get_product
from app.crud.sales_order import get_sales_order
from app.database import get_db
from app.schemas.after_sales import (
    AFTER_SALES_STATUSES,
    AFTER_SALES_TYPES,
    AfterSales,
    AfterSalesCreate,
    AfterSalesStatusUpdate,
)

router = APIRouter(prefix="/after-sales", tags=["after-sales"])
sales_router = APIRouter(prefix="/sales-orders", tags=["after-sales"])


def _validate_serials(
    db: Session,
    item,
    product,
    *,
    require_status: str,
    field: str,
    label: str,
) -> None:
    # 共用校验：某组序列号必填、数量一致、不重复、属于该商品、状态符合要求
    serials = getattr(item, field) or []
    if not serials:
        raise HTTPException(
            status_code=400,
            detail=f"商品(product_id={item.product_id})启用序列号管理，{label}必填",
        )
    if len(serials) != item.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"商品(product_id={item.product_id}){label}数量({len(serials)})与售后数量({item.quantity})不一致",
        )
    if len(set(serials)) != len(serials):
        raise HTTPException(status_code=400, detail=f"{label}列表中存在重复")
    for serial in serials:
        record = get_serial_by_number(db, serial)
        if record is None:
            raise HTTPException(status_code=400, detail=f"序列号 {serial} 不存在")
        if record.product_id != item.product_id:
            raise HTTPException(
                status_code=400, detail=f"序列号 {serial} 不属于商品(product_id={item.product_id})"
            )
        if record.status != require_status:
            raise HTTPException(
                status_code=400,
                detail=f"序列号 {serial} 当前状态({record.status})，{label}要求为 {require_status}",
            )


# POST /after-sales —— 创建售后单
@router.post("", response_model=AfterSales, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("after_sales", "create"))])
def create(data: AfterSalesCreate, db: Session = Depends(get_db)):
    if not data.items:
        raise HTTPException(status_code=400, detail="售后明细不能为空")
    # 售后单必须关联原订单，不能独立创建
    order = get_sales_order(db, data.original_order_id)
    if order is None:
        raise HTTPException(status_code=400, detail="原销售订单不存在")
    if get_customer(db, data.customer_id) is None:
        raise HTTPException(status_code=400, detail="客户不存在")
    if data.type not in AFTER_SALES_TYPES:
        raise HTTPException(status_code=400, detail="售后类型错误，可选 return/exchange/repair")

    # 原订单里卖过的商品，售后才允许出现
    ordered_product_ids = {item.product_id for item in order.items}

    for item in data.items:
        product = get_product(db, item.product_id)
        if product is None:
            raise HTTPException(
                status_code=400, detail=f"商品不存在（product_id={item.product_id}）"
            )
        if item.product_id not in ordered_product_ids:
            raise HTTPException(
                status_code=400,
                detail=f"商品(product_id={item.product_id})不在原订单中，不能售后",
            )
        if not product.enable_serial_tracking:
            # 非序列号商品：换货需要给出新批次并校验库存
            if data.type == "exchange":
                if not item.new_batch_number:
                    raise HTTPException(
                        status_code=400,
                        detail=f"商品(product_id={item.product_id})换货需传 new_batch_number",
                    )
                inventory = get_inventory_by_key(
                    db,
                    product_id=item.product_id,
                    warehouse_id=order.warehouse_id,
                    batch_number=item.new_batch_number,
                )
                current = inventory.quantity if inventory is not None else 0
                if current < item.quantity:
                    raise HTTPException(
                        status_code=400,
                        detail=f"商品(product_id={item.product_id})批次({item.new_batch_number})库存不足，当前 {current}",
                    )
            continue

        # ---- 序列号管理商品 ----
        if data.type != "repair":
            # 退货/换货：退回序列号必须是已售出的（sold）
            _validate_serials(
                db, item, product,
                require_status="sold", field="serial_numbers", label="退回序列号",
            )
        else:
            # 维修：送修序列号也必须是已售出的（sold）
            _validate_serials(
                db, item, product,
                require_status="sold", field="serial_numbers", label="送修序列号",
            )

        if data.type == "exchange":
            # 换货发出的新序列号：必须是库里可用的（available）
            _validate_serials(
                db, item, product,
                require_status="available", field="new_serial_numbers", label="换货新序列号",
            )
            overlap = set(item.serial_numbers or []) & set(item.new_serial_numbers or [])
            if overlap:
                raise HTTPException(status_code=400, detail="退回与换货新序列号不能有交集")

    return create_after_sales(db, data)


# GET /after-sales —— 售后单列表（可按 order_id 过滤）
@router.get("", response_model=list[AfterSales], dependencies=[Depends(require_permission("after_sales", "view"))])
def list_after_sales(
    order_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return get_after_sales_list(db, skip=skip, limit=limit, order_id=order_id)


# GET /after-sales/{after_sales_id} —— 详情
@router.get("/{after_sales_id}", response_model=AfterSales, dependencies=[Depends(require_permission("after_sales", "view"))])
def read(after_sales_id: int, db: Session = Depends(get_db)):
    after = get_after_sales(db, after_sales_id)
    if after is None:
        raise HTTPException(status_code=404, detail="售后单不存在")
    return after


# PUT /after-sales/{after_sales_id} —— 状态更新
@router.put("/{after_sales_id}", response_model=AfterSales, dependencies=[Depends(require_permission("after_sales", "edit"))])
def update_status(
    after_sales_id: int,
    data: AfterSalesStatusUpdate,
    db: Session = Depends(get_db),
):
    if data.status not in AFTER_SALES_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="状态错误，可选 pending/processing/completed/rejected",
        )
    after = update_after_sales_status(db, after_sales_id, data.status)
    if after is None:
        raise HTTPException(status_code=404, detail="售后单不存在")
    return after


# GET /sales-orders/{order_id}/after-sales —— 某销售订单的所有售后单
@sales_router.get("/{order_id}/after-sales", response_model=list[AfterSales], dependencies=[Depends(require_permission("after_sales", "view"))])
def after_sales_by_order(order_id: int, db: Session = Depends(get_db)):
    if get_sales_order(db, order_id) is None:
        raise HTTPException(status_code=404, detail="销售订单不存在")
    return get_after_sales_list(db, order_id=order_id)