# CRUD 包：封装数据库的增删改查操作
# 每个模块对应一张表，例如 unit.py 负责 Unit 表的读写
# 这样路由层（routers）不用直接写 SQL / ORM 查询，职责更清晰