# 销售出库单的数据库操作 + 库存扣减 + 序列号状态更新 + 订单状态更新
# 核心流程：
#   1. 生成出库单号
#   2. 建出库单主表 + 明细
#   3. 序列号管理商品 -> 对应 SerialInventory 状态 available 改为 sold
#   4. 按"商品+仓库+批次"扣减 Inventory 数量（不足则 400）
#   5. 更新销售订单状态（completed / partial）
#
# 注意：序列号归属/库存是否充足等校验放在路由层（router），
#      这里只是"执行"，但扣减会做二次兜底，防止负库存。

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from collections import Counter

from fastapi import HTTPException

from app.crud.inventory import get_inventory_by_key, get_serial_by_number
from app.crud.numbering import generate_serial_number
from app.models import (
    Product,
    SalesOrder,
    SalesOrderItem,
    SalesShipment,
    SalesShipmentItem,
)
from app.schemas.sales_shipment import SalesShipmentCreate


def get_sales_shipment(db: Session, shipment_id: int) -> SalesShipment | None:
    return (
        db.query(SalesShipment)
        .options(selectinload(SalesShipment.items))
        .filter(SalesShipment.id == shipment_id)
        .first()
    )


def get_shipped_quantities(db: Session, order_id: int) -> dict[int, int]:
    # 汇总某销售订单下每个商品已经累计出库的数量
    # 返回 {product_id: 已出库数量}
    rows = (
        db.query(SalesShipmentItem.product_id, func.sum(SalesShipmentItem.quantity))
        .join(SalesShipment, SalesShipmentItem.shipment_id == SalesShipment.id)
        .filter(SalesShipment.order_id == order_id)
        .group_by(SalesShipmentItem.product_id)
        .all()
    )
    return {product_id: int(total) for product_id, total in rows}


def _update_order_status(db: Session, order_id: int) -> None:
    # 汇总该订单的已出库数量，与销售数量比较，刷新订单状态
    order = db.get(SalesOrder, order_id)
    if order is None:
        return

    all_done = True  # 是否全部出库
    any_shipped = False  # 是否已经有部分出库

    items = (
        db.query(SalesOrderItem)
        .filter(SalesOrderItem.order_id == order_id)
        .all()
    )
    for item in items:
        shipped = (
            db.query(func.coalesce(func.sum(SalesShipmentItem.quantity), 0))
            .join(SalesShipment, SalesShipmentItem.shipment_id == SalesShipment.id)
            .filter(
                SalesShipment.order_id == order_id,
                SalesShipmentItem.product_id == item.product_id,
            )
            .scalar()
        )
        if shipped < item.quantity:
            all_done = False
        if shipped > 0:
            any_shipped = True

    if all_done:
        order.status = "completed"
    elif any_shipped:
        order.status = "partial"
    # 一条都没出库时保持 pending（正常流程不会走到）
    # 注意：收款状态 payment_status 保持不动，收款操作后续单独做


def _deduct_inventory(
    db: Session,
    *,
    product_id: int,
    warehouse_id: int,
    batch_number: str | None,
    quantity: int,
) -> None:
    # 按 商品+仓库+批次 扣减库存，不足则 400（路由已预校验，这里是兜底）
    inventory = get_inventory_by_key(
        db,
        product_id=product_id,
        warehouse_id=warehouse_id,
        batch_number=batch_number,
    )
    if inventory is None or inventory.quantity < quantity:
        raise HTTPException(
            status_code=400,
            detail=f"商品(product_id={product_id})批次({batch_number or '空'})库存不足",
        )
    inventory.quantity -= quantity


def create_sales_shipment(db: Session, data: SalesShipmentCreate) -> SalesShipment:
    # 1. 生成出库单号，如 SS20260918001
    shipment_number = generate_serial_number(
        db, SalesShipment, SalesShipment.shipment_number, "SS"
    )

    # 2. 创建出库单主表，flush 拿到 id
    shipment = SalesShipment(
        shipment_number=shipment_number,
        order_id=data.order_id,
        warehouse_id=data.warehouse_id,
        remark=data.remark,
    )
    db.add(shipment)
    db.flush()

    # 3. 批量创建出库明细 + 写序列号状态 + 扣减库存
    for item in data.items:
        db.add(
            SalesShipmentItem(
                shipment_id=shipment.id,
                product_id=item.product_id,
                quantity=item.quantity,
                batch_number=item.batch_number,
                serial_numbers=item.serial_numbers,
            )
        )

        product = db.get(Product, item.product_id)
        # 序列号管理商品：选中的序列号状态 available -> sold
        # 注：序列号归属校验由路由层完成保证
        if product is not None and product.enable_serial_tracking:
            serials = item.serial_numbers or []
            for serial in serials:
                serial_record = get_serial_by_number(db, serial)
                if serial_record is None:
                    raise HTTPException(status_code=400, detail=f"序列号 {serial} 不存在")
                serial_record.status = "sold"
            # 按序列号自身的批次分组扣减 Inventory（出库明细可能不传 batch_number，
            # 但序列号的批次是"入库时定死"的，用它来扣对应的库存批次更准确）
            batch_counts: Counter = Counter()
            for serial in serials:
                serial_record = get_serial_by_number(db, serial)
                batch_counts[serial_record.batch_number] += 1
            for batch, count in batch_counts.items():
                _deduct_inventory(
                    db,
                    product_id=item.product_id,
                    warehouse_id=data.warehouse_id,
                    batch_number=batch,
                    quantity=count,
                )
        else:
            # 普通商品：按明细里的批次扣减
            _deduct_inventory(
                db,
                product_id=item.product_id,
                warehouse_id=data.warehouse_id,
                batch_number=item.batch_number,
                quantity=item.quantity,
            )

    # 4. 先 flush：把刚 add 的出库明细写进事务，确保下面的统计查询能看到本次出库
    db.flush()

    # 5. 更新订单状态（completed / partial）；收款状态不动
    _update_order_status(db, data.order_id)

    db.commit()
    return get_sales_shipment(db, shipment.id)