# 维修记录接口
#   POST /after-sales/{id}/repair-records   给某售后单新增维修记录
#   PUT  /repair-records/{id}               更新维修记录（状态/费用等）

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.deps import require_permission
from sqlalchemy.orm import Session

from app.crud.after_sales import get_after_sales
from app.crud.repair_record import create_repair_record, update_repair_record
from app.database import get_db
from app.schemas.repair_record import (
    REPAIR_STATUSES,
    RepairRecord,
    RepairRecordCreate,
    RepairRecordUpdate,
)

router = APIRouter(prefix="/after-sales", tags=["repair-records"])
records_router = APIRouter(prefix="/repair-records", tags=["repair-records"])


# POST /after-sales/{after_sales_id}/repair-records —— 新增维修记录
@router.post(
    "/{after_sales_id}/repair-records",
    response_model=RepairRecord,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("after_sales", "create"))],
)
def create(
    after_sales_id: int,
    data: RepairRecordCreate,
    db: Session = Depends(get_db),
):
    after = get_after_sales(db, after_sales_id)
    if after is None:
        raise HTTPException(status_code=404, detail="售后单不存在")
    if data.status not in REPAIR_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="维修状态错误，可选 received/inspecting/repairing/shipped",
        )
    return create_repair_record(db, after_sales_id, data)


# PUT /repair-records/{record_id} —— 更新维修记录
@records_router.put("/{record_id}", response_model=RepairRecord, dependencies=[Depends(require_permission("after_sales", "edit"))])
def update(record_id: int, data: RepairRecordUpdate, db: Session = Depends(get_db)):
    if data.status is not None and data.status not in REPAIR_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="维修状态错误，可选 received/inspecting/repairing/shipped",
        )
    record = update_repair_record(db, record_id, data)
    if record is None:
        raise HTTPException(status_code=404, detail="维修记录不存在")
    return record