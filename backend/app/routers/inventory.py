# 库存相关接口
#   GET /inventories/serials?product_id=&warehouse_id=   查询某商品某仓库下的可用序列号

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.deps import require_permission
from sqlalchemy.orm import Session

from app.crud.inventory import get_available_serials
from app.crud.warehouse import get_warehouse
from app.crud.product import get_product
from app.database import get_db
from app.schemas.inventory import AvailableSerialsResponse

router = APIRouter(prefix="/inventories", tags=["inventories"])


# GET /inventories/serials —— 可用序列号列表
@router.get("/serials", response_model=AvailableSerialsResponse, dependencies=[Depends(require_permission("inventory", "view"))])
def available_serials(
    product_id: int,
    warehouse_id: int,
    db: Session = Depends(get_db),
):
    if get_product(db, product_id) is None:
        raise HTTPException(status_code=400, detail="商品不存在")
    if get_warehouse(db, warehouse_id) is None:
        raise HTTPException(status_code=400, detail="仓库不存在")
    serials = get_available_serials(db, product_id, warehouse_id)
    return {
        "product_id": product_id,
        "warehouse_id": warehouse_id,
        "serials": serials,
    }