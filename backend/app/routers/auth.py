# 认证接口
#   POST /auth/login   登录：用户名+密码 -> 返回 JWT token + 用户信息
#   GET  /auth/me      用 token 换当前用户信息

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.security import create_access_token, verify_password
from app.crud.user import get_user_by_username
from app.database import get_db
from app.models import User
from app.schemas.user import User as UserSchema
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    token_type: str = "bearer"
    user: UserSchema


# POST /auth/login —— 登录
@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_username(db, data.username)
    # 用户名不存在 / 密码不对 / 被禁用，统一返回 401（不泄露具体原因）
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误"
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号已被禁用")

    token = create_access_token(user.id, user.username, user.role_id)
    return LoginResponse(token=token, user=user)


# GET /auth/me —— 当前登录用户信息
@router.get("/me", response_model=UserSchema)
def me(current_user: User = Depends(get_current_user)):
    return current_user