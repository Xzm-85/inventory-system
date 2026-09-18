# 采购入库单的数据库操作 + 库存更新 + 序列号库存 + 订单状态更新
# 核心流程：
#   1. 生成入库单号
#   2. 建入库主表 + 明细
#   3. 商品启用序列号管理 -> 每个序列号写入 SerialInventory（状态 available）
#   4. 按"商品+仓库+批次"累加 Inventory 数量
#   5. 重新计算订单已入库数量，更新订单状态（completed / partial）
#
# 注意：序列号是否必填、数量是否一致、是否重复等校验放在路由层（router）
#      这里的 db.flush() 是为了让统计查询能看到刚 add 未提交的数据

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.crud.inventory import add_serial_record, upsert_inventory
from app.crud.numbering import generate_serial_number
from app.models import (
    Product,
    PurchaseOrder,
    PurchaseOrderItem,
    PurchaseReceipt,
    PurchaseReceiptItem,
)
from app.schemas.purchase_receipt import PurchaseReceiptCreate


def get_purchase_receipt(db: Session, receipt_id: int) -> PurchaseReceipt | None:
    return (
        db.query(PurchaseReceipt)
        .options(selectinload(PurchaseReceipt.items))
        .filter(PurchaseReceipt.id == receipt_id)
        .first()
    )


def get_received_quantities(
    db: Session, order_id: int
) -> dict[int, int]:
    # 汇总某订单下每个商品已经累计入库的数量
    # 返回 {product_id: 已入库数量}
    rows = (
        db.query(PurchaseReceiptItem.product_id, func.sum(PurchaseReceiptItem.quantity))
        .join(PurchaseReceipt, PurchaseReceiptItem.receipt_id == PurchaseReceipt.id)
        .filter(PurchaseReceipt.order_id == order_id)
        .group_by(PurchaseReceiptItem.product_id)
        .all()
    )
    return {product_id: int(total) for product_id, total in rows}


def _update_order_status(db: Session, order_id: int) -> None:
    # 汇总该订单的已入库数量，与采购数量比较，刷新订单状态
    order = db.get(PurchaseOrder, order_id)
    if order is None:
        return

    all_done = True  # 是否全部入库完成
    any_received = False  # 是否已经有部分入库

    items = (
        db.query(PurchaseOrderItem)
        .filter(PurchaseOrderItem.order_id == order_id)
        .all()
    )
    for item in items:
        # 该商品累计入库数量（跨所有入库单求和）
        received = (
            db.query(func.coalesce(func.sum(PurchaseReceiptItem.quantity), 0))
            .join(PurchaseReceipt, PurchaseReceiptItem.receipt_id == PurchaseReceipt.id)
            .filter(
                PurchaseReceipt.order_id == order_id,
                PurchaseReceiptItem.product_id == item.product_id,
            )
            .scalar()
        )
        if received < item.quantity:
            all_done = False
        if received > 0:
            any_received = True

    if all_done:
        order.status = "completed"
    elif any_received:
        order.status = "partial"
    # 一条都没入库时保持 pending（正常流程不会走到）


def create_purchase_receipt(db: Session, data: PurchaseReceiptCreate) -> PurchaseReceipt:
    # 1. 生成入库单号，如 PR20260918001
    receipt_number = generate_serial_number(
        db, PurchaseReceipt, PurchaseReceipt.receipt_number, "PR"
    )

    # 2. 创建入库单主表，flush 拿到 id
    receipt = PurchaseReceipt(
        receipt_number=receipt_number,
        order_id=data.order_id,
        warehouse_id=data.warehouse_id,
        remark=data.remark,
    )
    db.add(receipt)
    db.flush()

    # 3. 批量创建入库明细 + 写库存/序列号库存
    for item in data.items:
        db.add(
            PurchaseReceiptItem(
                receipt_id=receipt.id,
                product_id=item.product_id,
                quantity=item.quantity,
                batch_number=item.batch_number,
                serial_numbers=item.serial_numbers,
                production_date=item.production_date,
                expiry_date=item.expiry_date,
            )
        )

        product = db.get(Product, item.product_id)
        # 序列号管理商品：每个序列号单独写一行，状态 available
        # 注：序列号必填 / 数量必须等于 quantity / 查重 由路由层校验
        if product is not None and product.enable_serial_tracking:
            for serial in item.serial_numbers or []:
                add_serial_record(
                    db,
                    product_id=item.product_id,
                    warehouse_id=data.warehouse_id,
                    serial_number=serial,
                    batch_number=item.batch_number,
                )

        # 无论是否序列号管理，都累加原有 Inventory 表数量
        upsert_inventory(
            db,
            product_id=item.product_id,
            warehouse_id=data.warehouse_id,
            batch_number=item.batch_number,
            quantity=item.quantity,
        )

    # 4. 先 flush：把刚 add 的入库明细写进事务，确保下面的统计查询能看到本次入库
    db.flush()

    # 5. 更新订单状态（completed / partial）
    _update_order_status(db, data.order_id)

    db.commit()
    return get_purchase_receipt(db, receipt.id)