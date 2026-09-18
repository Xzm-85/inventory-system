# 商品相关接口
#   POST   /products        新增
#   GET    /products        列表
#   GET    /products/{id}   按 id 查询
#   PUT    /products/{id}   更新
#   DELETE /products/{id}   删除

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.category import get_category
from app.crud.product import (
    create_product,
    delete_product,
    get_product,
    get_products,
    update_product,
)
from app.crud.unit import get_unit
from app.database import get_db
from app.schemas.product import Product, ProductCreate, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])


# POST /products —— 新增商品
@router.post("", response_model=Product, status_code=status.HTTP_201_CREATED)
def create(data: ProductCreate, db: Session = Depends(get_db)):
    # 传了 category_id 就必须是真实存在的分类
    if data.category_id is not None and get_category(db, data.category_id) is None:
        raise HTTPException(status_code=400, detail="分类不存在")
    # 传了 unit_id 就必须是真实存在的单位
    if data.unit_id is not None and get_unit(db, data.unit_id) is None:
        raise HTTPException(status_code=400, detail="单位不存在")
    return create_product(db, data)


# GET /products —— 商品列表
@router.get("", response_model=list[Product])
def list_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_products(db, skip=skip, limit=limit)


# GET /products/{product_id} —— 按 id 查询
@router.get("/{product_id}", response_model=Product)
def read(product_id: int, db: Session = Depends(get_db)):
    product = get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product


# PUT /products/{product_id} —— 更新（只更新传了的字段）
@router.put("/{product_id}", response_model=Product)
def update(product_id: int, data: ProductUpdate, db: Session = Depends(get_db)):
    product = update_product(db, product_id, data)
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product


# DELETE /products/{product_id} —— 删除（会连带删除该商品的价格）
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(product_id: int, db: Session = Depends(get_db)):
    if not delete_product(db, product_id):
        raise HTTPException(status_code=404, detail="商品不存在")