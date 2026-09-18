# 仓库相关接口
#   POST   /warehouses        新增
#   GET    /warehouses        列表
#   GET    /warehouses/{id}   按 id 查询
#   PUT    /warehouses/{id}   更新
#   DELETE /warehouses/{id}   删除

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.warehouse import (
    create_warehouse,
    delete_warehouse,
    get_warehouse,
    get_warehouse_by_name,
    get_warehouses,
    update_warehouse,
)
from app.database import get_db
from app.schemas.warehouse import Warehouse, WarehouseCreate, WarehouseUpdate

router = APIRouter(prefix="/warehouses", tags=["warehouses"])


# POST /warehouses —— 新增，名称重复则 400
@router.post("", response_model=Warehouse, status_code=status.HTTP_201_CREATED)
def create(data: WarehouseCreate, db: Session = Depends(get_db)):
    if get_warehouse_by_name(db, data.name) is not None:
        raise HTTPException(status_code=400, detail="仓库名称已存在")
    return create_warehouse(db, data)


# GET /warehouses —— 列表
@router.get("", response_model=list[Warehouse])
def list_warehouses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_warehouses(db, skip=skip, limit=limit)


# GET /warehouses/{warehouse_id} —— 按 id 查询
@router.get("/{warehouse_id}", response_model=Warehouse)
def read(warehouse_id: int, db: Session = Depends(get_db)):
    warehouse = get_warehouse(db, warehouse_id)
    if warehouse is None:
        raise HTTPException(status_code=404, detail="仓库不存在")
    return warehouse


# PUT /warehouses/{warehouse_id} —— 更新，改名时查重
@router.put("/{warehouse_id}", response_model=Warehouse)
def update(warehouse_id: int, data: WarehouseUpdate, db: Session = Depends(get_db)):
    if data.name is not None:
        existing = get_warehouse_by_name(db, data.name)
        if existing is not None and existing.id != warehouse_id:
            raise HTTPException(status_code=400, detail="仓库名称已存在")
    warehouse = update_warehouse(db, warehouse_id, data)
    if warehouse is None:
        raise HTTPException(status_code=404, detail="仓库不存在")
    return warehouse


# DELETE /warehouses/{warehouse_id} —— 删除
@router.delete("/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(warehouse_id: int, db: Session = Depends(get_db)):
    if not delete_warehouse(db, warehouse_id):
        raise HTTPException(status_code=404, detail="仓库不存在")