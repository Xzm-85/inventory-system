# 依赖注入：鉴权（谁在调用）+ 权限（这个角色能不能干这事）
# 用法示例：
#   @router.get("/products")
#   def list_products(db=Depends(get_db), current=Depends(get_current_user)):
#       ...
#
#   限制到某模块某操作时：
#   @router.post("/products", dependencies=[Depends(require_permission("product", "create"))])
#   def create_product(...):
#       ...

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.crud.user import get_user
from app.database import get_db
from app.models import User

# 从 Authorization: Bearer <token> 里取 token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    # 解析 token -> 拿到 user_id -> 查库 -> 返回当前用户；失败一律 401
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="登录已失效，请重新登录",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    try:
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError):
        raise credentials_exception

    user = get_user(db, user_id)
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def require_permission(module: str, action: str):
    # 权限校验依赖工厂：生成一个依赖，检查当前用户角色的 module + action 权限
    # action 取值：view / create / edit / delete
    # 特判：admin 是超级管理员，直接放行，不查权限表，
    #       因此以后新增模块也不用回头给 admin 补权限。

    def permission_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        # admin 超级管理员直接放行
        if current_user.role.name == "admin":
            return current_user

        # 其他角色：查"角色权限表"
        permission = current_user.role.permissions
        if permission is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"角色[{current_user.role.name}]没有[{module}]模块权限",
            )

        allowed_map = {
            "view": lambda p: p.module == module and p.can_view,
            "create": lambda p: p.module == module and p.can_create,
            "edit": lambda p: p.module == module and p.can_edit,
            "delete": lambda p: p.module == module and p.can_delete,
        }
        checker = allowed_map.get(action)
        if checker is None:
            raise HTTPException(status_code=400, detail=f"未知权限操作: {action}")

        for perm in permission:
            if checker(perm):
                return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足：需要[{module}]模块的[{action}]权限",
        )

    return permission_checker