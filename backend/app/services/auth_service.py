# backend/app/services/auth_service.py
from datetime import datetime, timedelta
import os
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.user import User

# 从环境变量读取更安全，这里给一个默认值，方便开发环境使用
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 天

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, email: str, password: str, full_name: str | None = None) -> User:
    existing = get_user_by_email(db, email=email)
    if existing:
        raise ValueError("该邮箱已经注册")

    hashed_pw = get_password_hash(password)
    user = User(email=email, hashed_password=hashed_pw, full_name=full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    メールアドレスとパスワードでユーザー認証を行う
    - 存在しない場合：None
    - パスワード不一致：None
    - 停止中ユーザー（is_active = False）：None
    """
    user = get_user_by_email(db, email)
    if not user:
        return None

    # ❌ 停止中ユーザーはログイン不可
    if not user.is_active:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user



def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
