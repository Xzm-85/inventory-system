# 客户表的数据库操作（CRUD）

from sqlalchemy.orm import Session

from app.models import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


def get_customer(db: Session, customer_id: int) -> Customer | None:
    return db.get(Customer, customer_id)


def get_customer_by_name(db: Session, name: str) -> Customer | None:
    # 按名称查一条，用于新增/更新时的查重
    return db.query(Customer).filter(Customer.name == name).first()


def get_customers(db: Session, skip: int = 0, limit: int = 100) -> list[Customer]:
    return db.query(Customer).offset(skip).limit(limit).all()


def create_customer(db: Session, data: CustomerCreate) -> Customer:
    customer = Customer(**data.model_dump())  # 把请求数据展开成字段
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def update_customer(db: Session, customer_id: int, data: CustomerUpdate) -> Customer | None:
    customer = db.get(Customer, customer_id)
    if customer is None:
        return None
    # exclude_unset=True：只更新前端"实际传了"的字段
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return customer


def delete_customer(db: Session, customer_id: int) -> bool:
    customer = db.get(Customer, customer_id)
    if customer is None:
        return False
    db.delete(customer)
    db.commit()
    return True