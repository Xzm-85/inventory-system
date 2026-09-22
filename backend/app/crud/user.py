# 用户表的数据库操作
# 密码必须经过哈希后才能写入 password_hash，全程不落明文

from sqlalchemy.orm import Session, selectinload

from app.core.security import hash_password
from app.models import User
from app.schemas.user import UserCreate, UserUpdate


def get_user(db: Session, user_id: int) -> User | None:
    return (
        db.query(User)
        .options(selectinload(User.role))
        .filter(User.id == user_id)
        .first()
    )


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return (
        db.query(User)
        .options(selectinload(User.role))
        .order_by(User.id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_user(db: Session, data: UserCreate) -> User:
    user = User(
        username=data.username,
        password_hash=hash_password(data.password),  # 只存哈希
        real_name=data.real_name,
        role_id=data.role_id,
        is_active=data.is_active,
    )
    db.add(user)
    db.commit()
    return get_user(db, user.id)


def update_user(db: Session, user_id: int, data: UserUpdate) -> User | None:
    user = db.get(User, user_id)
    if user is None:
        return None
    if data.password is not None:
        user.password_hash = hash_password(data.password)
    if data.real_name is not None:
        user.real_name = data.real_name
    if data.role_id is not None:
        user.role_id = data.role_id
    if data.is_active is not None:
        user.is_active = data.is_active
    db.commit()
    return get_user(db, user.id)


def delete_user(db: Session, user_id: int) -> bool:
    user = db.get(User, user_id)
    if user is None:
        return False
    db.delete(user)
    db.commit()
    return True