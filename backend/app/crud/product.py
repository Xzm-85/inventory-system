# 商品表的数据库操作（CRUD）

from sqlalchemy.orm import Session

from app.models import Product
from app.schemas.product import ProductCreate, ProductUpdate


def get_product(db: Session, product_id: int) -> Product | None:
    return db.get(Product, product_id)


def get_products(db: Session, skip: int = 0, limit: int = 100) -> list[Product]:
    return db.query(Product).offset(skip).limit(limit).all()


def create_product(db: Session, data: ProductCreate) -> Product:
    # model_dump() 把 Schema 对象转成普通字典，再用 ** 展开成关键字参数
    # 等价于 Product(name=..., specification=..., ...) 逐个传入
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product_id: int, data: ProductUpdate) -> Product | None:
    product = db.get(Product, product_id)
    if product is None:
        return None
    # exclude_unset=True：只取前端"实际传了"的字段，没传的不动
    # 这样就能实现"局部更新"
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)  # setattr 等价于 product.field = value
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int) -> bool:
    product = db.get(Product, product_id)
    if product is None:
        return False
    db.delete(product)  # 关联的价格会因 cascade 配置被一并删除
    db.commit()
    return True