# 客户相关接口
#   POST   /customers        新增
#   GET    /customers        列表
#   GET    /customers/{id}   按 id 查询
#   PUT    /customers/{id}   更新
#   DELETE /customers/{id}   删除

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.customer import (
    create_customer,
    delete_customer,
    get_customer,
    get_customer_by_name,
    get_customers,
    update_customer,
)
from app.database import get_db
from app.schemas.customer import Customer, CustomerCreate, CustomerUpdate

router = APIRouter(prefix="/customers", tags=["customers"])


# POST /customers —— 新增，名称重复则 400
@router.post("", response_model=Customer, status_code=status.HTTP_201_CREATED)
def create(data: CustomerCreate, db: Session = Depends(get_db)):
    if get_customer_by_name(db, data.name) is not None:
        raise HTTPException(status_code=400, detail="客户名称已存在")
    return create_customer(db, data)


# GET /customers —— 列表
@router.get("", response_model=list[Customer])
def list_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_customers(db, skip=skip, limit=limit)


# GET /customers/{customer_id} —— 按 id 查询
@router.get("/{customer_id}", response_model=Customer)
def read(customer_id: int, db: Session = Depends(get_db)):
    customer = get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="客户不存在")
    return customer


# PUT /customers/{customer_id} —— 更新，改名时查重
@router.put("/{customer_id}", response_model=Customer)
def update(customer_id: int, data: CustomerUpdate, db: Session = Depends(get_db)):
    if data.name is not None:
        existing = get_customer_by_name(db, data.name)
        if existing is not None and existing.id != customer_id:
            raise HTTPException(status_code=400, detail="客户名称已存在")
    customer = update_customer(db, customer_id, data)
    if customer is None:
        raise HTTPException(status_code=404, detail="客户不存在")
    return customer


# DELETE /customers/{customer_id} —— 删除
@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(customer_id: int, db: Session = Depends(get_db)):
    if not delete_customer(db, customer_id):
        raise HTTPException(status_code=404, detail="客户不存在")