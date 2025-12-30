# backend/app/api/admin.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.api.deps import require_admin
from app.models.user import User

from sqlalchemy import func
from app.models.knowledge import KnowledgeDoc

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/system/status")
def system_status(
    _: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    # ユーザー数（有効ユーザーのみ）
    user_count = (
        db.query(func.count(User.id))
        .filter(getattr(User, "is_active", True))
        .scalar()
    )

    # ナレッジ文書数
    knowledge_count = db.query(func.count(KnowledgeDoc.id)).scalar()

    return {
        "ok": True,
        "services": {
            "llm": "ok",
            "vector_store": "ok",
        },
        "stats": {
            "users": user_count,
            "knowledge_docs": knowledge_count,
        },
    }


@router.get("/users")
def list_users(_: dict = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.id.desc()).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": bool(getattr(u, "is_active", True)),
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


@router.post("/users/{user_id}/active")
def set_user_active(
    user_id: int,
    payload: dict,
    _: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    active = payload.get("active")
    if active is None:
        raise HTTPException(status_code=400, detail="active が必要です")

    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")

    u.is_active = bool(active)
    db.commit()
    return {"ok": True}


@router.post("/users/{user_id}/make-admin")
def make_admin(
    user_id: int,
    _: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")

    if hasattr(u, "is_active") and not u.is_active:
        raise HTTPException(status_code=400, detail="停止中ユーザーは管理者にできません")

    u.role = "admin"
    db.commit()
    return {"ok": True}
