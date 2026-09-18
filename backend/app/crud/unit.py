# 单位表的数据库操作（CRUD = 增 Create / 查 Read / 改 Update / 删 Delete）
# 这一层只负责"读写数据库"，不处理 HTTP 状态码，保持职责单一

from sqlalchemy.orm import Session

from app.models import Unit
from app.schemas.unit import UnitCreate, UnitUpdate


# 按 id 查一条。返回 Unit 或 None（没查到）
def get_unit(db: Session, unit_id: int) -> Unit | None:
    return db.get(Unit, unit_id)


# 按名称查一条：用于新增/更新时的查重
def get_unit_by_name(db: Session, name: str) -> Unit | None:
    return db.query(Unit).filter(Unit.name == name).first()


# 查列表：skip 跳过多少条、limit 最多取多少条（分页用，类似 SQL 的 LIMIT/OFFSET）
def get_units(db: Session, skip: int = 0, limit: int = 100) -> list[Unit]:
    return db.query(Unit).offset(skip).limit(limit).all()


def create_unit(db: Session, data: UnitCreate) -> Unit:
    unit = Unit(name=data.name)  # 用请求数据构造模型对象
    db.add(unit)  # 加入会话（类似暂存）
    db.commit()  # 提交，真正写入数据库
    db.refresh(unit)  # 刷新，从数据库取回自增 id、创建时间等字段
    return unit


def update_unit(db: Session, unit_id: int, data: UnitUpdate) -> Unit | None:
    unit = db.get(Unit, unit_id)
    if unit is None:
        return None  # 不存在，返回 None，由路由层转成 404
    if data.name is not None:  # 只更新传了值的字段
        unit.name = data.name
    db.commit()
    db.refresh(unit)
    return unit


def delete_unit(db: Session, unit_id: int) -> bool:
    unit = db.get(Unit, unit_id)
    if unit is None:
        return False  # 不存在，返回 False
    db.delete(unit)
    db.commit()
    return True