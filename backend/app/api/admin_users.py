# backend/app/api/admin_users.py
# 管理者向け：ユーザー一覧 / 権限変更 / 停止

from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.api.deps import require_admin
from app.models.user import User

router = APIRouter(prefix="/admin/users", tags=["admin-users"])


class UserItem(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: Optional[str] = None


@router.get("", response_model=List[UserItem])
def list_users(_: dict = Depends(require_admin), db: Session = Depends(get_db)):
    """
    ユーザー一覧
    """
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [
        UserItem(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            role=u.role,
            is_active=u.is_active,
            created_at=u.created_at.isoformat() if u.created_at else None,
        )
        for u in users
    ]


class RoleUpdate(BaseModel):
    role: str  # "user" or "admin"


@router.patch("/{user_id}/role", response_model=UserItem)
def update_role(
    user_id: int,
    payload: RoleUpdate,
    _: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    権限変更（admin / user）
    """
    if payload.role not in ("user", "admin"):
        raise HTTPException(status_code=400, detail="role は 'user' または 'admin'")

    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません。")

    u.role = payload.role
    db.commit()
    db.refresh(u)

    return UserItem(
        id=u.id,
        email=u.email,
        full_name=u.full_name,
        role=u.role,
        is_active=u.is_active,
        created_at=u.created_at.isoformat() if u.created_at else None,
    )


class ActiveUpdate(BaseModel):
    is_active: bool


@router.patch("/{user_id}/active", response_model=UserItem)
def update_active(
    user_id: int,
    payload: ActiveUpdate,
    _: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    ユーザー停止/再開
    """
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません。")

    u.is_active = bool(payload.is_active)
    db.commit()
    db.refresh(u)

    return UserItem(
        id=u.id,
        email=u.email,
        full_name=u.full_name,
        role=u.role,
        is_active=u.is_active,
        created_at=u.created_at.isoformat() if u.created_at else None,
    )
