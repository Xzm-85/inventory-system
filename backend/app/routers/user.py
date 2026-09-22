# 用户接口（仅 admin 角色可操作）
#   POST   /users         创建用户
#   GET    /users         用户列表
#   GET    /users/{id}    用户详情
#   PUT    /users/{id}    更新（改密码/角色/状态）
#   DELETE /users/{id}    删除

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import require_permission
from app.crud.role import get_role
from app.crud.user import (
    create_user,
    delete_user,
    get_user,
    get_user_by_username,
    get_users,
    update_user,
)
from app.database import get_db
from app.schemas.user import User, UserCreate, UserUpdate

router = APIRouter(
    prefix="/users", tags=["users"], dependencies=[Depends(require_permission("user", "view"))]
)


# POST /users —— 创建用户
@router.post("", response_model=User, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_permission("user", "create"))])
def create(data: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, data.username) is not None:
        raise HTTPException(status_code=400, detail="用户名已存在")
    if get_role(db, data.role_id) is None:
        raise HTTPException(status_code=400, detail="角色不存在")
    return create_user(db, data)


# GET /users —— 列表
@router.get("", response_model=list[User])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_users(db, skip=skip, limit=limit)


# GET /users/{user_id} —— 详情
@router.get("/{user_id}", response_model=User)
def read(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


# PUT /users/{user_id} —— 更新
@router.put("/{user_id}", response_model=User,
            dependencies=[Depends(require_permission("user", "edit"))])
def update(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    if data.role_id is not None and get_role(db, data.role_id) is None:
        raise HTTPException(status_code=400, detail="角色不存在")
    user = update_user(db, user_id, data)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


# DELETE /users/{user_id} —— 删除
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_permission("user", "delete"))])
def delete(user_id: int, db: Session = Depends(get_db)):
    # 不允许删除最后一个 admin 账号，防止系统没有管理员
    user = get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.username == "admin":
        raise HTTPException(status_code=400, detail="不能删除内置管理员账号")
    delete_user(db, user_id)