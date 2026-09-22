# 销售出库接口
#   POST /sales-shipments   创建出库单（自动校验库存/序列号 + 扣减库存 + 更新订单状态）

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.deps import require_permission
from sqlalchemy.orm import Session

from app.crud.inventory import get_inventory_by_key, get_serial_by_number
from app.crud.product import get_product
from app.crud.sales_order import get_sales_order
from app.crud.sales_shipment import (
    create_sales_shipment,
    get_shipped_quantities,
    get_sales_shipment,
)
from app.crud.warehouse import get_warehouse
from app.database import get_db
from app.schemas.sales_shipment import SalesShipment, SalesShipmentCreate

router = APIRouter(prefix="/sales-shipments", tags=["sales-shipments"])


def _validate_serials(db: Session, item, product, warehouse_id: int) -> None:
    # 序列号管理商品的出库校验：
    #   1. serial_numbers 必填
    #   2. 数量必须与 quantity 一致
    #   3. 列表内不能有重复
    #   4. 序列号必须属于该商品、该仓库，且状态为 available
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
            detail=f"商品(product_id={item.product_id})序列号数量({len(serials)})与出库数量({item.quantity})不一致",
        )
    if len(set(serials)) != len(serials):
        raise HTTPException(status_code=400, detail="序列号列表中存在重复")
    for serial in serials:
        record = get_serial_by_number(db, serial)
        if record is None:
            raise HTTPException(status_code=400, detail=f"序列号 {serial} 不存在")
        if record.product_id != item.product_id:
            raise HTTPException(
                status_code=400,
                detail=f"序列号 {serial} 不属于商品(product_id={item.product_id})",
            )
        if record.warehouse_id != warehouse_id:
            raise HTTPException(
                status_code=400,
                detail=f"序列号 {serial} 不在该仓库（warehouse_id={warehouse_id}）",
            )
        if record.status != "available":
            raise HTTPException(status_code=400, detail=f"序列号 {serial} 当前不可出库（状态：{record.status}）")


def _check_inventory(
    db: Session, item, product, warehouse_id: int
) -> None:
    # 非序列号商品：按"商品+仓库+批次"校验库存是否充足
    if product.enable_serial_tracking:
        return
    inventory = get_inventory_by_key(
        db,
        product_id=item.product_id,
        warehouse_id=warehouse_id,
        batch_number=item.batch_number,
    )
    if inventory is None or inventory.quantity < item.quantity:
        current = inventory.quantity if inventory is not None else 0
        raise HTTPException(
            status_code=400,
            detail=f"商品(product_id={item.product_id})批次({item.batch_number or '空'})库存不足，当前 {current}，需出库 {item.quantity}",
        )


# POST /sales-shipments —— 创建出库单
@router.post("", response_model=SalesShipment, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("sales", "create"))])
def create(data: SalesShipmentCreate, db: Session = Depends(get_db)):
    if not data.items:
        raise HTTPException(status_code=400, detail="出库明细不能为空")
    order = get_sales_order(db, data.order_id)
    if order is None:
        raise HTTPException(status_code=400, detail="销售订单不存在")
    if order.status == "completed":
        raise HTTPException(status_code=400, detail="该订单已全部出库，不能再出库")
    if get_warehouse(db, data.warehouse_id) is None:
        raise HTTPException(status_code=400, detail="仓库不存在")

    # 查该订单的销售数量与已出库数量，防止超量出库
    ordered = {item.product_id: item.quantity for item in order.items}
    shipped = get_shipped_quantities(db, data.order_id)

    for item in data.items:
        product = get_product(db, item.product_id)
        if product is None:
            raise HTTPException(
                status_code=400, detail=f"商品不存在（product_id={item.product_id}）"
            )
        remaining = ordered.get(item.product_id, 0) - shipped.get(item.product_id, 0)
        if item.quantity > remaining:
            raise HTTPException(
                status_code=400,
                detail=f"商品(product_id={item.product_id})超量出库，剩余可出库 {remaining}，本次 {item.quantity}",
            )
        # 序列号管理商品：序列号校验
        _validate_serials(db, item, product, data.warehouse_id)
        # 非序列号商品：库存充足校验
        _check_inventory(db, item, product, data.warehouse_id)

    return create_sales_shipment(db, data)