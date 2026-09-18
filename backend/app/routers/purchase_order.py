# 采购订单接口
#   POST /purchase-orders        创建采购订单（带 items 明细）
#   GET  /purchase-orders        查询订单列表
#   GET  /purchase-orders/{id}   查询订单详情（含明细）

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.purchase_order import (
    create_purchase_order,
    get_purchase_order,
    get_purchase_orders,
)
from app.crud.supplier import get_supplier
from app.crud.warehouse import get_warehouse
from app.crud.product import get_product
from app.database import get_db
from app.schemas.purchase_order import PurchaseOrder, PurchaseOrderCreate

router = APIRouter(prefix="/purchase-orders", tags=["purchase-orders"])


# POST /purchase-orders —— 创建采购订单
@router.post("", response_model=PurchaseOrder, status_code=status.HTTP_201_CREATED)
def create(data: PurchaseOrderCreate, db: Session = Depends(get_db)):
    if not data.items:
        raise HTTPException(status_code=400, detail="采购明细不能为空")
    if get_supplier(db, data.supplier_id) is None:
        raise HTTPException(status_code=400, detail="供应商不存在")
    if get_warehouse(db, data.warehouse_id) is None:
        raise HTTPException(status_code=400, detail="仓库不存在")
    for item in data.items:
        if get_product(db, item.product_id) is None:
            raise HTTPException(status_code=400, detail=f"商品不存在（product_id={item.product_id}）")
    return create_purchase_order(db, data)


# GET /purchase-orders —— 订单列表（含明细）
@router.get("", response_model=list[PurchaseOrder])
def list_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_purchase_orders(db, skip=skip, limit=limit)


# GET /purchase-orders/{order_id} —— 订单详情
@router.get("/{order_id}", response_model=PurchaseOrder)
def read(order_id: int, db: Session = Depends(get_db)):
    order = get_purchase_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="采购订单不存在")
    return order