# 安全相关工具：密码哈希（bcrypt）+ JWT 生成/解析
# 密码绝不存明文，只存 passlib 生成的 bcrypt 哈希
# token 用 python-jose 生成 HS256 签名

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import ALGORITHM, SECRET_KEY, TOKEN_EXPIRE_MINUTES

# bcrypt 密码上下文，统一入口
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    # 明文 -> 哈希（随机盐，每次相同密码结果不同）
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    # 校验输入的明文密码是否匹配存储的哈希
    return pwd_context.verify(password, password_hash)


def create_access_token(user_id: int, username: str, role_id: int) -> str:
    # 生成 JWT：payload 里带 user_id / username / role_id 和过期时间
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "username": username,
        "role_id": role_id,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    # 解析并校验 token 签名/过期时间，失败返回 None
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None