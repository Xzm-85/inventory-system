# 角色权限的数据库操作

from sqlalchemy.orm import Session, selectinload

from app.models import Role, RolePermission
from app.schemas.role_permission import RolePermissionBatch


def get_permissions_by_role(db: Session, role_id: int) -> list[RolePermission]:
    return (
        db.query(RolePermission)
        .filter(RolePermission.role_id == role_id)
        .order_by(RolePermission.id.asc())
        .all()
    )


def set_permissions(
    db: Session, role_id: int, data: RolePermissionBatch
) -> list[RolePermission]:
    # 整体替换：先删掉该角色旧权限，再按请求批量写入
    db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
    db.flush()
    for perm in data.permissions:
        db.add(
            RolePermission(
                role_id=role_id,
                module=perm.module,
                can_view=perm.can_view,
                can_create=perm.can_create,
                can_edit=perm.can_edit,
                can_delete=perm.can_delete,
            )
        )
    db.commit()
    return get_permissions_by_role(db, role_id)