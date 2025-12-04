"""安全工具 - 密码哈希和 JWT Token 处理"""
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import jwt, JWTError
from passlib.context import CryptContext

from .config import auth_config

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建 Access Token

    Args:
        data: Token 载荷数据，通常包含 {"sub": user_id}
        expires_delta: 自定义过期时间

    Returns:
        JWT Token 字符串
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=auth_config.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({
        "exp": expire,
        "type": auth_config.TOKEN_TYPE_ACCESS,
        "iat": datetime.utcnow()
    })
    return jwt.encode(to_encode, auth_config.SECRET_KEY, algorithm=auth_config.ALGORITHM)


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    创建 Refresh Token

    Args:
        data: Token 载荷数据，通常包含 {"sub": user_id}

    Returns:
        JWT Token 字符串
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=auth_config.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "type": auth_config.TOKEN_TYPE_REFRESH,
        "iat": datetime.utcnow()
    })
    return jwt.encode(to_encode, auth_config.SECRET_KEY, algorithm=auth_config.ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    解码并验证 JWT Token

    Args:
        token: JWT Token 字符串

    Returns:
        解码后的载荷数据，如果验证失败返回 None
    """
    try:
        payload = jwt.decode(
            token,
            auth_config.SECRET_KEY,
            algorithms=[auth_config.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def hash_token(token: str) -> str:
    """
    对 Token 进行哈希（用于存储 Refresh Token）

    Args:
        token: Token 字符串

    Returns:
        Token 的 SHA-256 哈希值
    """
    return hashlib.sha256(token.encode()).hexdigest()


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    验证密码强度

    Args:
        password: 密码字符串

    Returns:
        (是否有效, 错误消息)
    """
    if len(password) < auth_config.PASSWORD_MIN_LENGTH:
        return False, f"密码长度至少 {auth_config.PASSWORD_MIN_LENGTH} 个字符"

    # 可以添加更多验证规则
    # has_upper = any(c.isupper() for c in password)
    # has_lower = any(c.islower() for c in password)
    # has_digit = any(c.isdigit() for c in password)

    return True, ""
