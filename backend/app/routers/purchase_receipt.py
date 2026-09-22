# 采购入库接口
#   POST /purchase-receipts   创建入库单（自动累加库存 + 更新订单状态）

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.deps import require_permission
from sqlalchemy.orm import Session

from app.crud.inventory import get_serial_by_number
from app.crud.product import get_product
from app.crud.purchase_order import get_purchase_order
from app.crud.purchase_receipt import create_purchase_receipt, get_received_quantities
from app.crud.warehouse import get_warehouse
from app.database import get_db
from app.models import PurchaseOrderItem
from app.schemas.purchase_receipt import PurchaseReceipt, PurchaseReceiptCreate

router = APIRouter(prefix="/purchase-receipts", tags=["purchase-receipts"])


def _validate_serials(db: Session, item, product) -> None:
    # 序列号管理商品的入库校验：
    #   1. serial_numbers 必填
    #   2. 数量必须与 quantity 一致
    #   3. 列表内不能有重复
    #   4. 全局不能与已有序列号重复
    if not product.enable_serial_tracking:
        return

    serials = item.serial_numbers or []
    if not serials:
        raise HTTPException(
            status_code=400,
            detail=f"商品(product_id={item.product_id})启用序列号管理，serial_numbers 必填",
        )
    if len(serials) != item.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"商品(product_id={item.product_id})序列号数量({len(serials)})与入库数量({item.quantity})不一致",
        )
    if len(set(serials)) != len(serials):
        raise HTTPException(status_code=400, detail=f"序列号列表中存在重复")
    for serial in serials:
        if get_serial_by_number(db, serial) is not None:
            raise HTTPException(status_code=400, detail=f"序列号 {serial} 已存在，不能重复入库")


# POST /purchase-receipts —— 创建入库单
@router.post("", response_model=PurchaseReceipt, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("purchase", "create"))])
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
        product = get_product(db, item.product_id)
        if product is None:
            raise HTTPException(
                status_code=400, detail=f"商品不存在（product_id={item.product_id}）"
            )
        remaining = ordered.get(item.product_id, 0) - received.get(item.product_id, 0)
        if item.quantity > remaining:
            raise HTTPException(
                status_code=400,
                detail=f"商品(product_id={item.product_id})超量入库，剩余可入库 {remaining}，本次 {item.quantity}",
            )
        # 序列号管理商品的序列号校验（必填/数量一致/查重）
        _validate_serials(db, item, product)

    return create_purchase_receipt(db, data)