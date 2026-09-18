# 单号生成工具：PO/PR 共用的"编号生成器"
# 规则：前缀 + 年月日 + 3位序号，例如 PO20260918001
# 实现方式：查当天已存在的最大编号，序号 +1（不存在则从 001 开始）

from datetime import datetime

from sqlalchemy.orm import Session


def generate_serial_number(db: Session, model, column, prefix: str) -> str:
    today = datetime.now().strftime("%Y%m%d")  # 当天日期，如 20260918
    prefix_pattern = f"{prefix}{today}%"  # 匹配 PO20260918*
    last = (
        db.query(column)
        .filter(column.like(prefix_pattern))
        .order_by(column.desc())  # 取当天最大的编号
        .limit(1)
        .scalar()
    )
    if last:
        seq = int(str(last)[-3:]) + 1  # 末尾 3 位序号 +1
    else:
        seq = 1
    return f"{prefix}{today}{seq:03d}"