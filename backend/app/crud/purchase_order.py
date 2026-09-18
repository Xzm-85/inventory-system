# 采购订单的数据库操作
# 创建时：先生成订单编号 -> 建主表 -> 批量建明细 -> 算小计/总金额

from decimal import Decimal

from sqlalchemy.orm import Session, selectinload

from app.crud.numbering import generate_serial_number
from app.models import PurchaseOrder, PurchaseOrderItem
from app.schemas.purchase_order import PurchaseOrderCreate


def get_purchase_order(db: Session, order_id: int) -> PurchaseOrder | None:
    # selectinload：一次性把明细 items 一起查出来，避免后续逐条查询数据库
    return (
        db.query(PurchaseOrder)
        .options(selectinload(PurchaseOrder.items))
        .filter(PurchaseOrder.id == order_id)
        .first()
    )


def get_purchase_orders(db: Session, skip: int = 0, limit: int = 100) -> list[PurchaseOrder]:
    return (
        db.query(PurchaseOrder)
        .options(selectinload(PurchaseOrder.items))
        .order_by(PurchaseOrder.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_purchase_order(db: Session, data: PurchaseOrderCreate) -> PurchaseOrder:
    # 1. 生成订单编号，如 PO20260918001
    order_number = generate_serial_number(db, PurchaseOrder, PurchaseOrder.order_number, "PO")

    # 2. 创建主表（先 flush 拿到自增 id，才能给明细关联 order_id）
    order = PurchaseOrder(
        order_number=order_number,
        supplier_id=data.supplier_id,
        warehouse_id=data.warehouse_id,
        status="pending",
        remark=data.remark,
        total_amount=Decimal("0"),
    )
    db.add(order)
    db.flush()

    # 3. 批量创建明细，计算每条小计，累计总金额
    total_amount = Decimal("0")
    for item in data.items:
        subtotal = item.quantity * item.unit_price  # 小计 = 数量 × 单价
        total_amount += subtotal
        db.add(
            PurchaseOrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=subtotal,
            )
        )

    # 4. 回填总金额并提交
    order.total_amount = total_amount
    db.commit()

    # 5. 重新查询（带明细），返回给前端
    return get_purchase_order(db, order.id)