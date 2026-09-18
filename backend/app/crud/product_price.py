# 商品价格表的数据库操作

from sqlalchemy.orm import Session

from app.models import ProductPrice
from app.schemas.product_price import ProductPriceCreate


def create_product_price(db: Session, data: ProductPriceCreate) -> ProductPrice:
    # 把请求数据展开成字段，构造并保存一条价格记录
    price = ProductPrice(**data.model_dump())
    db.add(price)
    db.commit()
    db.refresh(price)
    return price


def get_prices_by_product(
    db: Session, product_id: int, skip: int = 0, limit: int = 100
) -> list[ProductPrice]:
    # 按商品 id 过滤，查出该商品的所有价格（可能有多条：零售/批发/采购）
    return (
        db.query(ProductPrice)
        .filter(ProductPrice.product_id == product_id)
        .offset(skip)
        .limit(limit)
        .all()
    )