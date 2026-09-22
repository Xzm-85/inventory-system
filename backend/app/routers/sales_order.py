# 销售订单接口
#   POST /sales-orders        创建订单（自动算小计/总金额）
#   GET  /sales-orders        列表
#   GET  /sales-orders/{id}   详情

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.deps import require_permission
from sqlalchemy.orm import Session

from app.crud.customer import get_customer
from app.crud.payment_method import get_payment_method
from app.crud.product import get_product
from app.crud.sales_order import create_sales_order, get_sales_order, get_sales_orders
from app.crud.warehouse import get_warehouse
from app.database import get_db
from app.schemas.sales_order import SalesOrder, SalesOrderCreate

router = APIRouter(prefix="/sales-orders", tags=["sales-orders"])


# POST /sales-orders —— 创建销售订单
@router.post("", response_model=SalesOrder, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("sales", "create"))])
def create(data: SalesOrderCreate, db: Session = Depends(get_db)):
    if not data.items:
        raise HTTPException(status_code=400, detail="销售明细不能为空")
    if get_customer(db, data.customer_id) is None:
        raise HTTPException(status_code=400, detail="客户不存在")
    if get_warehouse(db, data.warehouse_id) is None:
        raise HTTPException(status_code=400, detail="仓库不存在")
    if get_payment_method(db, data.payment_method_id) is None:
        raise HTTPException(status_code=400, detail="收款方式不存在")
    for item in data.items:
        if get_product(db, item.product_id) is None:
            raise HTTPException(
                status_code=400, detail=f"商品不存在（product_id={item.product_id}）"
            )
    return create_sales_order(db, data)


# GET /sales-orders —— 列表
@router.get("", response_model=list[SalesOrder], dependencies=[Depends(require_permission("sales", "view"))])
def list_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_sales_orders(db, skip=skip, limit=limit)


# GET /sales-orders/{order_id} —— 详情
@router.get("/{order_id}", response_model=SalesOrder, dependencies=[Depends(require_permission("sales", "view"))])
def read(order_id: int, db: Session = Depends(get_db)):
    order = get_sales_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="销售订单不存在")
    return order