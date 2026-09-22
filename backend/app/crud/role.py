# 角色表的数据库操作

from sqlalchemy.orm import Session

from app.models import Role
from app.schemas.role import RoleCreate, RoleUpdate


def get_role(db: Session, role_id: int) -> Role | None:
    return db.get(Role, role_id)


def get_role_by_name(db: Session, name: str) -> Role | None:
    return db.query(Role).filter(Role.name == name).first()


def get_roles(db: Session, skip: int = 0, limit: int = 100) -> list[Role]:
    return (
        db.query(Role)
        .order_by(Role.id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_role(db: Session, data: RoleCreate) -> Role:
    role = Role(name=data.name, description=data.description)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def update_role(db: Session, role_id: int, data: RoleUpdate) -> Role | None:
    role = db.get(Role, role_id)
    if role is None:
        return None
    if data.name is not None:
        role.name = data.name
    if data.description is not None:
        role.description = data.description
    db.commit()
    db.refresh(role)
    return role


def delete_role(db: Session, role_id: int) -> bool:
    role = db.get(Role, role_id)
    if role is None:
        return False
    db.delete(role)
    db.commit()
    return True