# 维修记录的数据库操作

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import RepairRecord
from app.schemas.repair_record import RepairRecordCreate, RepairRecordUpdate


def create_repair_record(
    db: Session, after_sales_id: int, data: RepairRecordCreate
) -> RepairRecord:
    record = RepairRecord(
        after_sales_id=after_sales_id,
        status=data.status,
        fault_description=data.fault_description,
        repair_action=data.repair_action,
        cost=data.cost if data.cost is not None else Decimal("0"),
        is_under_warranty=data.is_under_warranty,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_repair_record(
    db: Session, record_id: int, data: RepairRecordUpdate
) -> RepairRecord | None:
    record = db.get(RepairRecord, record_id)
    if record is None:
        return None
    if data.status is not None:
        record.status = data.status
    if data.fault_description is not None:
        record.fault_description = data.fault_description
    if data.repair_action is not None:
        record.repair_action = data.repair_action
    if data.cost is not None:
        record.cost = data.cost
    if data.is_under_warranty is not None:
        record.is_under_warranty = data.is_under_warranty
    db.commit()
    db.refresh(record)
    return record