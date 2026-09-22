# 角色权限接口（仅 admin 可操作）
#   GET  /roles/{role_id}/permissions   查某角色所有权限
#   PUT  /roles/{role_id}/permissions   批量设置某角色权限（整体替换）

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import require_permission
from app.crud.role import get_role
from app.crud.role_permission import get_permissions_by_role, set_permissions
from app.database import get_db
from app.schemas.role_permission import (
    RolePermission,
    RolePermissionBatch,
)

router = APIRouter(
    prefix="/roles", tags=["role-permissions"], dependencies=[Depends(require_permission("user", "view"))]
)


# GET /roles/{role_id}/permissions —— 查询角色权限
@router.get("/{role_id}/permissions", response_model=list[RolePermission])
def read_permissions(role_id: int, db: Session = Depends(get_db)):
    if get_role(db, role_id) is None:
        raise HTTPException(status_code=404, detail="角色不存在")
    return get_permissions_by_role(db, role_id)


# PUT /roles/{role_id}/permissions —— 批量设置（整体替换），仅 admin
@router.put("/{role_id}/permissions", response_model=list[RolePermission],
            dependencies=[Depends(require_permission("user", "edit"))])
def update_permissions(role_id: int, data: RolePermissionBatch, db: Session = Depends(get_db)):
    if get_role(db, role_id) is None:
        raise HTTPException(status_code=404, detail="角色不存在")
    if not data.permissions:
        raise HTTPException(status_code=400, detail="权限列表不能为空")
    return set_permissions(db, role_id, data)