# 单位相关接口
# 接口清单：
#   POST   /units        新增单位
#   GET    /units        查询单位列表
#   GET    /units/{id}   按 id 查询
#   PUT    /units/{id}   更新
#   DELETE /units/{id}   删除

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.deps import require_permission
from sqlalchemy.orm import Session

from app.crud.unit import (
    create_unit,
    delete_unit,
    get_unit,
    get_unit_by_name,
    get_units,
    update_unit,
)
from app.database import get_db
from app.schemas.unit import Unit, UnitCreate, UnitUpdate

# prefix="/units"：这个文件里所有接口都自动带 /units 前缀
# tags=["units"]：Swagger 文档里的分组名
router = APIRouter(prefix="/units", tags=["units"])


# POST /units —— 新增（201 Created）
@router.post("", response_model=Unit, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("product", "create"))])
def create(data: UnitCreate, db: Session = Depends(get_db)):
    # 查重：名称已存在就抛 400 错误，前端会收到 {"detail": "单位名称已存在"}
    if get_unit_by_name(db, data.name) is not None:
        raise HTTPException(status_code=400, detail="单位名称已存在")
    return create_unit(db, data)


# GET /units —— 列表（skip/limit 是 query 参数，如 /units?skip=0&limit=100）
@router.get("", response_model=list[Unit], dependencies=[Depends(require_permission("product", "view"))])
def list_units(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_units(db, skip=skip, limit=limit)


# GET /units/{unit_id} —— 按 id 查询；路径参数自动转成 int
@router.get("/{unit_id}", response_model=Unit, dependencies=[Depends(require_permission("product", "view"))])
def read(unit_id: int, db: Session = Depends(get_db)):
    unit = get_unit(db, unit_id)
    if unit is None:
        raise HTTPException(status_code=404, detail="单位不存在")
    return unit


# PUT /units/{unit_id} —— 更新
@router.put("/{unit_id}", response_model=Unit, dependencies=[Depends(require_permission("product", "edit"))])
def update(unit_id: int, data: UnitUpdate, db: Session = Depends(get_db)):
    # 改名时查重：如果新名称已被"别的单位"占用，则不允许
    if data.name is not None:
        existing = get_unit_by_name(db, data.name)
        if existing is not None and existing.id != unit_id:
            raise HTTPException(status_code=400, detail="单位名称已存在")
    unit = update_unit(db, unit_id, data)
    if unit is None:
        raise HTTPException(status_code=404, detail="单位不存在")
    return unit


# DELETE /units/{unit_id} —— 删除（204 表示成功且无返回内容）
@router.delete("/{unit_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("product", "delete"))])
def delete(unit_id: int, db: Session = Depends(get_db)):
    if not delete_unit(db, unit_id):
        raise HTTPException(status_code=404, detail="单位不存在")