# 分类相关接口（扁平结构，只有名称）
#   POST   /categories        新增分类
#   GET    /categories        分类列表
#   GET    /categories/{id}   按 id 查询
#   PUT    /categories/{id}   更新
#   DELETE /categories/{id}   删除

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.category import (
    create_category,
    delete_category,
    get_categories,
    get_category,
    get_category_by_name,
    update_category,
)
from app.database import get_db
from app.schemas.category import Category, CategoryCreate, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


# POST /categories —— 新增，名称重复则 400
@router.post("", response_model=Category, status_code=status.HTTP_201_CREATED)
def create(data: CategoryCreate, db: Session = Depends(get_db)):
    if get_category_by_name(db, data.name) is not None:
        raise HTTPException(status_code=400, detail="分类名称已存在")
    return create_category(db, data)


# GET /categories —— 列表
@router.get("", response_model=list[Category])
def list_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_categories(db, skip=skip, limit=limit)


# GET /categories/{category_id} —— 按 id 查询
@router.get("/{category_id}", response_model=Category)
def read(category_id: int, db: Session = Depends(get_db)):
    category = get_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category


# PUT /categories/{category_id} —— 更新，改名时查重
@router.put("/{category_id}", response_model=Category)
def update(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    if data.name is not None:
        existing = get_category_by_name(db, data.name)
        if existing is not None and existing.id != category_id:
            raise HTTPException(status_code=400, detail="分类名称已存在")
    category = update_category(db, category_id, data)
    if category is None:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category


# DELETE /categories/{category_id} —— 删除
@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(category_id: int, db: Session = Depends(get_db)):
    if not delete_category(db, category_id):
        raise HTTPException(status_code=404, detail="分类不存在")