# 角色接口（仅 admin 可操作）
#   POST   /roles         创建角色
#   GET    /roles         角色列表
#   GET    /roles/{id}    角色详情
#   PUT    /roles/{id}    更新角色
#   DELETE /roles/{id}    删除角色

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import require_permission
from app.crud.role import (
    create_role,
    delete_role,
    get_role,
    get_role_by_name,
    get_roles,
    update_role,
)
from app.database import get_db
from app.schemas.role import Role, RoleCreate, RoleUpdate

router = APIRouter(
    prefix="/roles", tags=["roles"], dependencies=[Depends(require_permission("user", "view"))]
)


# POST /roles —— 创建角色，名称重复则 400
@router.post("", response_model=Role, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_permission("user", "create"))])
def create(data: RoleCreate, db: Session = Depends(get_db)):
    if get_role_by_name(db, data.name) is not None:
        raise HTTPException(status_code=400, detail="角色名称已存在")
    return create_role(db, data)


# GET /roles —— 列表
@router.get("", response_model=list[Role])
def list_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_roles(db, skip=skip, limit=limit)


# GET /roles/{role_id} —— 详情
@router.get("/{role_id}", response_model=Role)
def read(role_id: int, db: Session = Depends(get_db)):
    role = get_role(db, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="角色不存在")
    return role


# PUT /roles/{role_id} —— 更新，改名时查重
@router.put("/{role_id}", response_model=Role,
            dependencies=[Depends(require_permission("user", "edit"))])
def update(role_id: int, data: RoleUpdate, db: Session = Depends(get_db)):
    if data.name is not None:
        existing = get_role_by_name(db, data.name)
        if existing is not None and existing.id != role_id:
            raise HTTPException(status_code=400, detail="角色名称已存在")
    role = update_role(db, role_id, data)
    if role is None:
        raise HTTPException(status_code=404, detail="角色不存在")
    return role


# DELETE /roles/{role_id} —— 删除
@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_permission("user", "delete"))])
def delete(role_id: int, db: Session = Depends(get_db)):
    role = get_role(db, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="角色不存在")
    if role.name == "admin":
        raise HTTPException(status_code=400, detail="不能删除内置管理员角色")
    if len(role.users) > 0:
        raise HTTPException(status_code=400, detail="该角色下还有用户，不能删除")
    delete_role(db, role_id)