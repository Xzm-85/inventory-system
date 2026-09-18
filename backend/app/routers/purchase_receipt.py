# 采购入库接口
#   POST /purchase-receipts   创建入库单（自动累加库存 + 更新订单状态）

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.product import get_product
from app.crud.purchase_order import get_purchase_order
from app.crud.purchase_receipt import create_purchase_receipt, get_received_quantities
from app.crud.warehouse import get_warehouse
from app.database import get_db
from app.models import PurchaseOrderItem
from app.schemas.purchase_receipt import PurchaseReceipt, PurchaseReceiptCreate

router = APIRouter(prefix="/purchase-receipts", tags=["purchase-receipts"])


# POST /purchase-receipts —— 创建入库单
@router.post("", response_model=PurchaseReceipt, status_code=status.HTTP_201_CREATED)
def create(data: PurchaseReceiptCreate, db: Session = Depends(get_db)):
    if not data.items:
        raise HTTPException(status_code=400, detail="入库明细不能为空")
    order = get_purchase_order(db, data.order_id)
    if order is None:
        raise HTTPException(status_code=400, detail="采购订单不存在")
    if order.status == "completed":
        raise HTTPException(status_code=400, detail="该订单已全部入库，不能再入库")
    if get_warehouse(db, data.warehouse_id) is None:
        raise HTTPException(status_code=400, detail="仓库不存在")

    # 查该订单的采购数量与已入库数量，防止超量入库
    ordered = {item.product_id: item.quantity for item in order.items}
    received = get_received_quantities(db, data.order_id)

    for item in data.items:
        if get_product(db, item.product_id) is None:
            raise HTTPException(
                status_code=400, detail=f"商品不存在（product_id={item.product_id}）"
            )
        remaining = ordered.get(item.product_id, 0) - received.get(item.product_id, 0)
        if item.quantity > remaining:
            raise HTTPException(
                status_code=400,
                detail=f"商品(product_id={item.product_id})超量入库，剩余可入库 {remaining}，本次 {item.quantity}",
            )

    return create_purchase_receipt(db, data)