# backend/app/api/admin_system.py
# 管理者向け：システム状態（最小）

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db import get_db
from app.models.user import User
from app.models.knowledge import KnowledgeDoc

router = APIRouter(prefix="/admin/system", tags=["admin-system"])


@router.get("/status")
def system_status(_: dict = Depends(require_admin), db: Session = Depends(get_db)):
    """
    システム状態（最小）
    """
    user_count = db.query(User).count()
    doc_count = db.query(KnowledgeDoc).count()

    return {
        "ok": True,
        "services": {
            "api": "ok",
            "db": "ok",
        },
        "stats": {
            "users": user_count,
            "knowledge_docs": doc_count,
        },
    }
