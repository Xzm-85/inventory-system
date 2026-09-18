# 分类表的数据库操作（CRUD）

from sqlalchemy.orm import Session

from app.models import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_category(db: Session, category_id: int) -> Category | None:
    return db.get(Category, category_id)


def get_category_by_name(db: Session, name: str) -> Category | None:
    # 按名称查一条，用于新增/更新时的查重
    return db.query(Category).filter(Category.name == name).first()


def get_categories(db: Session, skip: int = 0, limit: int = 100) -> list[Category]:
    # 分页查询分类列表
    return db.query(Category).offset(skip).limit(limit).all()


def create_category(db: Session, data: CategoryCreate) -> Category:
    category = Category(name=data.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category_id: int, data: CategoryUpdate) -> Category | None:
    category = db.get(Category, category_id)
    if category is None:
        return None
    if data.name is not None:
        category.name = data.name
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int) -> bool:
    category = db.get(Category, category_id)
    if category is None:
        return False
    db.delete(category)
    db.commit()
    return True