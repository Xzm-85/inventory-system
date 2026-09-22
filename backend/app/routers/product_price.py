# 商品价格相关接口
#   POST /product-prices              新增一条价格
#   GET  /product-prices?product_id=1 查询某个商品的所有价格

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.deps import require_permission
from sqlalchemy.orm import Session

from app.crud.product import get_product
from app.crud.product_price import create_product_price, get_prices_by_product
from app.database import get_db
from app.schemas.product_price import ProductPrice, ProductPriceCreate

router = APIRouter(prefix="/product-prices", tags=["product-prices"])


# POST /product-prices —— 新增价格，商品必须存在
@router.post("", response_model=ProductPrice, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("product", "create"))])
def create(data: ProductPriceCreate, db: Session = Depends(get_db)):
    if get_product(db, data.product_id) is None:
        raise HTTPException(status_code=400, detail="商品不存在")
    return create_product_price(db, data)


# GET /product-prices?product_id=... —— 按商品查询价格列表
# product_id 是 query 参数，不传会返回 400
@router.get("", response_model=list[ProductPrice], dependencies=[Depends(require_permission("product", "view"))])
def list_prices(
    product_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    if product_id is None:
        raise HTTPException(status_code=400, detail="请指定 product_id 参数")
    return get_prices_by_product(db, product_id, skip=skip, limit=limit)