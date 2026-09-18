# 健康检查接口：用于确认服务是否正常、数据库连接是否可用

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

# APIRouter 类似前端路由的一个"分组"，最后在 main.py 里统一挂载
router = APIRouter()


# @router.get("/health") 是装饰器：把下面的函数注册成 GET /health 接口
# Depends(get_db)：FastAPI 自动注入一个数据库会话（无需手动创建/关闭）
@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))  # 执行最简单的 SQL，能跑通说明数据库正常
    return {"status": "ok"}