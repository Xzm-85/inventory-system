# 供应商表的数据库操作（CRUD）

from sqlalchemy.orm import Session

from app.models import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate


def get_supplier(db: Session, supplier_id: int) -> Supplier | None:
    return db.get(Supplier, supplier_id)


def get_supplier_by_name(db: Session, name: str) -> Supplier | None:
    # 按名称查一条，用于新增/更新时的查重
    return db.query(Supplier).filter(Supplier.name == name).first()


def get_suppliers(db: Session, skip: int = 0, limit: int = 100) -> list[Supplier]:
    return db.query(Supplier).offset(skip).limit(limit).all()


def create_supplier(db: Session, data: SupplierCreate) -> Supplier:
    supplier = Supplier(**data.model_dump())  # 把请求数据展开成字段
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


def update_supplier(db: Session, supplier_id: int, data: SupplierUpdate) -> Supplier | None:
    supplier = db.get(Supplier, supplier_id)
    if supplier is None:
        return None
    # exclude_unset=True：只更新前端"实际传了"的字段
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(supplier, field, value)
    db.commit()
    db.refresh(supplier)
    return supplier


def delete_supplier(db: Session, supplier_id: int) -> bool:
    supplier = db.get(Supplier, supplier_id)
    if supplier is None:
        return False
    db.delete(supplier)
    db.commit()
    return True