# 数据库连接层：整个后端与 MySQL 打交道的地方都在这里统一配置
# 其他文件（crud / routers）都从这 import 需要的对象

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import DATABASE_URL

# 1. engine = "数据库引擎"，相当于和后端建立了一条通往 MySQL 的连接池
#    pool_pre_ping=True  ：每次取连接前先 ping 一下，防止用到"死掉"的连接
#    pool_recycle=3600    ：连接超过 1 小时自动回收重建，避免被 MySQL 端断开
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)

# 2. SessionLocal = "会话工厂"，每次操作数据库时用它创建一个"会话"
#    Session 在 SQLAlchemy 里类似前端的"数据连接/事务对象"：
#    增删改查都通过它执行，改完要 commit() 提交，否则不生效
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 3. Base = 所有模型（表）的"基类"
#    通俗讲：我们定义的每张表（Unit、Product 等）都必须继承 Base，
#    SQLAlchemy 才能认识它们、才能自动建表
class Base(DeclarativeBase):
    pass


# 4. get_db = 依赖注入函数（FastAPI 特色）
#    这是一个 python 的"生成器"（yield 关键字）。
#    每个接口请求进来时，FastAPI 会自动调用它开一个新的 Session，
#    接口执行完会自动关闭。相当于前端的"请求拦截器 + 资源释放"
def get_db():
    db = SessionLocal()  # 开一个会话（类似 new 一个 axios 实例）
    try:
        yield db  # 把会话交给接口使用
    finally:
        db.close()  # 无论接口成功失败，最后都会关掉会话