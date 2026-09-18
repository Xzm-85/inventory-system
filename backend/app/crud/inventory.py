# 库存表 + 序列号库存的数据库操作

from sqlalchemy.orm import Session

from app.models import Inventory, SerialInventory


def get_inventory_by_key(
    db: Session,
    *,
    product_id: int,
    warehouse_id: int,
    batch_number: str | None,
) -> Inventory | None:
    # 按"商品+仓库+批次"查库存记录
    # 注意：批次为空时用 is_(None) 判断（SQL 中 NULL = NULL 不成立）
    query = db.query(Inventory).filter(
        Inventory.product_id == product_id,
        Inventory.warehouse_id == warehouse_id,
    )
    if batch_number is None:
        query = query.filter(Inventory.batch_number.is_(None))
    else:
        query = query.filter(Inventory.batch_number == batch_number)
    return query.first()


def upsert_inventory(
    db: Session,
    *,
    product_id: int,
    warehouse_id: int,
    batch_number: str | None,
    quantity: int,
) -> None:
    # 已存在则累加数量，不存在则新建记录
    inventory = get_inventory_by_key(
        db,
        product_id=product_id,
        warehouse_id=warehouse_id,
        batch_number=batch_number,
    )
    if inventory is not None:
        inventory.quantity += quantity
    else:
        db.add(
            Inventory(
                product_id=product_id,
                warehouse_id=warehouse_id,
                batch_number=batch_number,
                quantity=quantity,
            )
        )


# ---------- 序列号库存 ----------

def get_serial_by_number(db: Session, serial_number: str) -> SerialInventory | None:
    # 序列号查重：全局唯一
    return (
        db.query(SerialInventory)
        .filter(SerialInventory.serial_number == serial_number)
        .first()
    )


def add_serial_record(
    db: Session,
    *,
    product_id: int,
    warehouse_id: int,
    serial_number: str,
    batch_number: str | None,
    status: str = "available",
) -> None:
    # 一个序列号写一行，状态默认 available
    db.add(
        SerialInventory(
            product_id=product_id,
            warehouse_id=warehouse_id,
            serial_number=serial_number,
            batch_number=batch_number,
            status=status,
        )
    )


def get_available_serials(
    db: Session, product_id: int, warehouse_id: int
) -> list[SerialInventory]:
    # 查某商品在某仓库下所有"可用"的序列号
    return (
        db.query(SerialInventory)
        .filter(
            SerialInventory.product_id == product_id,
            SerialInventory.warehouse_id == warehouse_id,
            SerialInventory.status == "available",
        )
        .order_by(SerialInventory.id)
        .all()
    )