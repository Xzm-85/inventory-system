# 配置文件：负责读取数据库连接信息
# 相当于前端的"全局配置常量"，只不过值来自环境变量 / .env 文件

import os

from dotenv import load_dotenv

# 读取项目根目录的 .env 文件（比如 backend/.env），把里面的配置加载进环境变量
load_dotenv()

# os.getenv("名字", "默认值")：取环境变量，如果没设置就用默认值
# 注意：这些值都是 .env 文件 / 环境变量里的字符串
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "inventory_db")

# 拼接成数据库连接地址（连接串 URL）
# 格式：mysql+pymysql://用户名:密码@主机:端口/库名?charset=utf8mb4
# utf8mb4 是为了支持中文和 emoji
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    "?charset=utf8mb4"
)