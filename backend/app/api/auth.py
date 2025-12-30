# backend/app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.services.auth_service import (
    create_user,
    authenticate_user,
    create_access_token,
    verify_password,
    get_password_hash,
)

from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


# ========= Pydantic 模型 =========

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MeResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    role: str


# ========= 接口实现 =========

@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """
    注册新用户
    """
    try:
        create_user(
            db=db,
            email=str(payload.email),          # ✅ 确保是纯字符串
            password=payload.password,
            full_name=payload.full_name,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return {"msg": "User created"}


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    OAuth2 标准登录（Swagger Authorize 会用这个）
    - Swagger 会提交 application/x-www-form-urlencoded
    - form_data.username 在这里就是“邮箱”
    """
    email = form_data.username
    password = form_data.password

    user = authenticate_user(db, email=email, password=password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱或密码错误",
        )

    # 建议 sub 用 email（更通用），也可以用 user.id（字符串化）
    token = create_access_token({"sub": user.email, "email": user.email})

    return TokenResponse(access_token=token, token_type="bearer")

@router.get("/me", response_model=MeResponse)
def me(current_user: User = Depends(get_current_user)):
    """
    ログイン中のユーザー情報を返す
    """
    return MeResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
    )

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    パスワード変更（本人のみ）
    """
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="現在のパスワードが正しくありません")

    current_user.hashed_password = get_password_hash(payload.new_password)
    db.add(current_user)
    db.commit()

    return {"ok": True}