# 收款方式的数据库操作

from sqlalchemy.orm import Session

from app.models import PaymentMethod
from app.schemas.payment_method import PaymentMethodCreate, PaymentMethodUpdate


def get_payment_method(db: Session, method_id: int) -> PaymentMethod | None:
    return db.get(PaymentMethod, method_id)


def get_payment_method_by_name(db: Session, name: str) -> PaymentMethod | None:
    return db.query(PaymentMethod).filter(PaymentMethod.name == name).first()


def get_payment_methods(db: Session, skip: int = 0, limit: int = 100) -> list[PaymentMethod]:
    return (
        db.query(PaymentMethod)
        .order_by(PaymentMethod.id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_payment_method(db: Session, data: PaymentMethodCreate) -> PaymentMethod:
    method = PaymentMethod(name=data.name, is_active=data.is_active)
    db.add(method)
    db.commit()
    db.refresh(method)
    return method


def update_payment_method(
    db: Session, method_id: int, data: PaymentMethodUpdate
) -> PaymentMethod | None:
    method = db.get(PaymentMethod, method_id)
    if method is None:
        return None
    if data.name is not None:
        method.name = data.name
    if data.is_active is not None:
        method.is_active = data.is_active
    db.commit()
    db.refresh(method)
    return method


def delete_payment_method(db: Session, method_id: int) -> bool:
    method = db.get(PaymentMethod, method_id)
    if method is None:
        return False
    db.delete(method)
    db.commit()
    return True