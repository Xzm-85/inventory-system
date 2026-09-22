# 收款方式相关接口
#   POST   /payment-methods         新增
#   GET    /payment-methods         列表
#   GET    /payment-methods/{id}    按 id 查询
#   PUT    /payment-methods/{id}    更新
#   DELETE /payment-methods/{id}    删除

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.deps import require_permission
from sqlalchemy.orm import Session

from app.crud.payment_method import (
    create_payment_method,
    delete_payment_method,
    get_payment_method,
    get_payment_method_by_name,
    get_payment_methods,
    update_payment_method,
)
from app.database import get_db
from app.schemas.payment_method import (
    PaymentMethod,
    PaymentMethodCreate,
    PaymentMethodUpdate,
)

router = APIRouter(prefix="/payment-methods", tags=["payment-methods"])


# POST /payment-methods —— 新增，名称重复则 400
@router.post("", response_model=PaymentMethod, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("payment", "create"))])
def create(data: PaymentMethodCreate, db: Session = Depends(get_db)):
    if get_payment_method_by_name(db, data.name) is not None:
        raise HTTPException(status_code=400, detail="收款方式名称已存在")
    return create_payment_method(db, data)


# GET /payment-methods —— 列表（可按 is_active 过滤已启用的）
@router.get("", response_model=list[PaymentMethod], dependencies=[Depends(require_permission("payment", "view"))])
def list_methods(
    active_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    methods = get_payment_methods(db, skip=skip, limit=limit)
    if active_only:
        methods = [m for m in methods if m.is_active]
    return methods


# GET /payment-methods/{method_id} —— 按 id 查询
@router.get("/{method_id}", response_model=PaymentMethod, dependencies=[Depends(require_permission("payment", "view"))])
def read(method_id: int, db: Session = Depends(get_db)):
    method = get_payment_method(db, method_id)
    if method is None:
        raise HTTPException(status_code=404, detail="收款方式不存在")
    return method


# PUT /payment-methods/{method_id} —— 更新，改名时查重
@router.put("/{method_id}", response_model=PaymentMethod, dependencies=[Depends(require_permission("payment", "edit"))])
def update(method_id: int, data: PaymentMethodUpdate, db: Session = Depends(get_db)):
    if data.name is not None:
        existing = get_payment_method_by_name(db, data.name)
        if existing is not None and existing.id != method_id:
            raise HTTPException(status_code=400, detail="收款方式名称已存在")
    method = update_payment_method(db, method_id, data)
    if method is None:
        raise HTTPException(status_code=404, detail="收款方式不存在")
    return method


# DELETE /payment-methods/{method_id} —— 删除
@router.delete("/{method_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("payment", "delete"))])
def delete(method_id: int, db: Session = Depends(get_db)):
    if not delete_payment_method(db, method_id):
        raise HTTPException(status_code=404, detail="收款方式不存在")