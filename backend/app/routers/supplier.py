# 供应商相关接口
#   POST   /suppliers        新增
#   GET    /suppliers        列表
#   GET    /suppliers/{id}   按 id 查询
#   PUT    /suppliers/{id}   更新
#   DELETE /suppliers/{id}   删除

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.supplier import (
    create_supplier,
    delete_supplier,
    get_supplier,
    get_supplier_by_name,
    get_suppliers,
    update_supplier,
)
from app.database import get_db
from app.schemas.supplier import Supplier, SupplierCreate, SupplierUpdate

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


# POST /suppliers —— 新增，名称重复则 400
@router.post("", response_model=Supplier, status_code=status.HTTP_201_CREATED)
def create(data: SupplierCreate, db: Session = Depends(get_db)):
    if get_supplier_by_name(db, data.name) is not None:
        raise HTTPException(status_code=400, detail="供应商名称已存在")
    return create_supplier(db, data)


# GET /suppliers —— 列表
@router.get("", response_model=list[Supplier])
def list_suppliers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_suppliers(db, skip=skip, limit=limit)


# GET /suppliers/{supplier_id} —— 按 id 查询
@router.get("/{supplier_id}", response_model=Supplier)
def read(supplier_id: int, db: Session = Depends(get_db)):
    supplier = get_supplier(db, supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="供应商不存在")
    return supplier


# PUT /suppliers/{supplier_id} —— 更新，改名时查重
@router.put("/{supplier_id}", response_model=Supplier)
def update(supplier_id: int, data: SupplierUpdate, db: Session = Depends(get_db)):
    if data.name is not None:
        existing = get_supplier_by_name(db, data.name)
        if existing is not None and existing.id != supplier_id:
            raise HTTPException(status_code=400, detail="供应商名称已存在")
    supplier = update_supplier(db, supplier_id, data)
    if supplier is None:
        raise HTTPException(status_code=404, detail="供应商不存在")
    return supplier


# DELETE /suppliers/{supplier_id} —— 删除
@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(supplier_id: int, db: Session = Depends(get_db)):
    if not delete_supplier(db, supplier_id):
        raise HTTPException(status_code=404, detail="供应商不存在")