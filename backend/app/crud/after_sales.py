# 售后单的数据库操作 + 三类售后的库存/序列号处理
#
#   return  退货：   序列号 sold -> available，Inventory 按序列号批次补回
#   exchange 换货：  退回序列号 sold -> available + 库存补回；
#                    发出序列号 available -> sold + 库存扣减
#   repair  维修：   序列号 sold -> repairing，库存不变；
#                    售后单 completed 后 repairing -> sold
#
# 所有售后单严格关联原销售订单，序列号校验在路由层完成，这里只执行。

from collections import Counter

from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload

from app.crud.inventory import get_inventory_by_key, get_serial_by_number, upsert_inventory
from app.crud.numbering import generate_serial_number
from app.models import AfterSalesItem, AfterSalesOrder, Product
from app.schemas.after_sales import AfterSalesCreate, AfterSalesItemCreate


def get_after_sales(db: Session, after_sales_id: int) -> AfterSalesOrder | None:
    # 一次性查明细 + 维修记录，避免逐条查询
    return (
        db.query(AfterSalesOrder)
        .options(
            selectinload(AfterSalesOrder.items),
            selectinload(AfterSalesOrder.repair_records),
        )
        .filter(AfterSalesOrder.id == after_sales_id)
        .first()
    )


def get_after_sales_list(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    order_id: int | None = None,
) -> list[AfterSalesOrder]:
    query = db.query(AfterSalesOrder).options(
        selectinload(AfterSalesOrder.items),
        selectinload(AfterSalesOrder.repair_records),
    )
    if order_id is not None:
        query = query.filter(AfterSalesOrder.original_order_id == order_id)
    return query.order_by(AfterSalesOrder.id.desc()).offset(skip).limit(limit).all()


def _add_serials_back(db: Session, product_id: int, serials: list[str]) -> None:
    # 退货/换货退回：把序列号对应的库存按"序列号自身批次"分组补回
    # 序列号记录里带着入库时的仓库和批次，用它作为回仓目标
    batch_counts: Counter = Counter()
    for serial in serials:
        record = get_serial_by_number(db, serial)
        batch_counts[(record.warehouse_id, record.batch_number)] += 1
    for (warehouse_id, batch), count in batch_counts.items():
        upsert_inventory(
            db,
            product_id=product_id,
            warehouse_id=warehouse_id,
            batch_number=batch,
            quantity=count,
        )


def _deduct_inventory(
    db: Session,
    *,
    product_id: int,
    warehouse_id: int,
    batch_number: str | None,
    quantity: int,
) -> None:
    # 换货发新：扣减库存（路由已校验充足，这里是兜底）
    inventory = get_inventory_by_key(
        db, product_id=product_id, warehouse_id=warehouse_id, batch_number=batch_number
    )
    if inventory is None or inventory.quantity < quantity:
        raise HTTPException(
            status_code=400,
            detail=f"商品(product_id={product_id})批次({batch_number or '空'})库存不足",
        )
    inventory.quantity -= quantity


def _handle_return(db: Session, item: AfterSalesItemCreate, order_warehouse_id: int) -> None:
    # 退货回仓
    if item.serial_numbers:
        for serial in item.serial_numbers:
            record = get_serial_by_number(db, serial)
            record.status = "available"  # sold -> available
        _add_serials_back(db, item.product_id, item.serial_numbers)
    else:
        # 非序列号商品：按明细批次回仓（仓库用原订单的发货仓库）
        upsert_inventory(
            db,
            product_id=item.product_id,
            warehouse_id=order_warehouse_id,
            batch_number=item.batch_number,
            quantity=item.quantity,
        )


def _handle_exchange(
    db: Session, item: AfterSalesItemCreate, order_warehouse_id: int
) -> None:
    # 换货 = 退旧 + 发新
    _handle_return(db, item, order_warehouse_id)

    # 发出新商品
    if item.new_serial_numbers:
        for serial in item.new_serial_numbers:
            record = get_serial_by_number(db, serial)
            record.status = "sold"  # available -> sold
        # 按新序列号自身批次扣减库存
        batch_counts: Counter = Counter()
        for serial in item.new_serial_numbers:
            record = get_serial_by_number(db, serial)
            batch_counts[(record.warehouse_id, record.batch_number)] += 1
        for (warehouse_id, batch), count in batch_counts.items():
            _deduct_inventory(
                db,
                product_id=item.product_id,
                warehouse_id=warehouse_id,
                batch_number=batch,
                quantity=count,
            )
    else:
        # 非序列号商品：从原订单发货仓库的新批次里扣减
        _deduct_inventory(
            db,
            product_id=item.product_id,
            warehouse_id=order_warehouse_id,
            batch_number=item.new_batch_number,
            quantity=item.quantity,
        )


def _handle_repair(db: Session, item: AfterSalesItemCreate) -> None:
    # 维修：只把序列号改为 repairing，库存不动
    for serial in item.serial_numbers or []:
        record = get_serial_by_number(db, serial)
        record.status = "repairing"  # sold -> repairing


def create_after_sales(db: Session, data: AfterSalesCreate) -> AfterSalesOrder:
    # 1. 生成售后单号，如 AS20260921001
    after_sales_number = generate_serial_number(
        db, AfterSalesOrder, AfterSalesOrder.after_sales_number, "AS"
    )

    # 2. 创建主表，flush 拿 id
    after = AfterSalesOrder(
        after_sales_number=after_sales_number,
        original_order_id=data.original_order_id,
        customer_id=data.customer_id,
        type=data.type,
        status="pending",  # 新售后单默认待处理
        reason=data.reason,
        remark=data.remark,
    )
    db.add(after)
    db.flush()

    # 原订单的发货仓库：非序列号商品的回仓/发新默认用它
    from app.models import SalesOrder

    order_warehouse_id = db.get(SalesOrder, data.original_order_id).warehouse_id

    # 3. 批量建明细 + 按类型处理库存/序列号
    for item in data.items:
        db.add(
            AfterSalesItem(
                after_sales_id=after.id,
                product_id=item.product_id,
                quantity=item.quantity,
                batch_number=item.batch_number,
                serial_numbers=item.serial_numbers,
                new_batch_number=item.new_batch_number,
                new_serial_numbers=item.new_serial_numbers,
            )
        )
        if data.type == "return":
            _handle_return(db, item, order_warehouse_id)
        elif data.type == "exchange":
            _handle_exchange(db, item, order_warehouse_id)
        elif data.type == "repair":
            _handle_repair(db, item)

    db.commit()
    return get_after_sales(db, after.id)


def update_after_sales_status(
    db: Session, after_sales_id: int, status: str
) -> AfterSalesOrder | None:
    after = db.get(AfterSalesOrder, after_sales_id)
    if after is None:
        return None
    # 维修单走到 completed 或 rejected：送修序列号从 repairing 改回 sold
    # （维修完成售后闭环，设备可用；拒绝则视为未送修，同样释放状态）
    if after.type == "repair" and status in ("completed", "rejected"):
        for item in after.items:
            for serial in item.serial_numbers or []:
                record = get_serial_by_number(db, serial)
                if record is not None and record.status == "repairing":
                    record.status = "sold"
    after.status = status
    db.commit()
    db.refresh(after)
    return get_after_sales(db, after.id)