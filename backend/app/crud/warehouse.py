# 仓库表的数据库操作（CRUD）

from sqlalchemy.orm import Session

from app.models import Warehouse
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate


def get_warehouse(db: Session, warehouse_id: int) -> Warehouse | None:
    return db.get(Warehouse, warehouse_id)


def get_warehouse_by_name(db: Session, name: str) -> Warehouse | None:
    # 按名称查一条，用于新增/更新时的查重
    return db.query(Warehouse).filter(Warehouse.name == name).first()


def get_warehouses(db: Session, skip: int = 0, limit: int = 100) -> list[Warehouse]:
    return db.query(Warehouse).offset(skip).limit(limit).all()


def create_warehouse(db: Session, data: WarehouseCreate) -> Warehouse:
    warehouse = Warehouse(**data.model_dump())  # 把请求数据展开成字段
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return warehouse


def update_warehouse(db: Session, warehouse_id: int, data: WarehouseUpdate) -> Warehouse | None:
    warehouse = db.get(Warehouse, warehouse_id)
    if warehouse is None:
        return None
    # exclude_unset=True：只更新前端"实际传了"的字段
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(warehouse, field, value)
    db.commit()
    db.refresh(warehouse)
    return warehouse


def delete_warehouse(db: Session, warehouse_id: int) -> bool:
    warehouse = db.get(Warehouse, warehouse_id)
    if warehouse is None:
        return False
    db.delete(warehouse)
    db.commit()
    return True