# backend/app/api/admin_knowledge.py
# 管理者向け：ナレッジ文書の追加/一覧/削除/再読み込み

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.api.deps import require_admin
from app.models.knowledge import KnowledgeDoc
from app.services.knowledge_service import reload_knowledge_cache

router = APIRouter(prefix="/admin/knowledge", tags=["admin-knowledge"])

ALLOWED_EXT = {".txt", ".md", ".markdown"}


def _safe_filename(name: str) -> str:
  name = name.replace("\\", "_").replace("/", "_").replace("..", "_").strip()
  return name or "upload.txt"


@router.get("", response_model=List[dict])
def list_docs(_: dict = Depends(require_admin), db: Session = Depends(get_db)):
  """
  アップロード済み文書一覧（DB 管理分）
  """
  docs = (
    db.query(KnowledgeDoc)
    .filter(KnowledgeDoc.status == "active")
    .order_by(KnowledgeDoc.created_at.desc())
    .all()
  )
  return [
    {
      "id": d.id,
      "original_name": d.original_name,
      "stored_name": d.stored_name,  # 互換のため残しているだけ
      "size": d.size,
      "content_type": d.content_type,
      "created_at": d.created_at.isoformat() if d.created_at else None,
    }
    for d in docs
  ]


@router.post("/upload", status_code=200)
async def upload_doc(
  _: dict = Depends(require_admin),
  db: Session = Depends(get_db),
  file: UploadFile = File(...),
):
  """
  文書アップロード → テキスト抽出 → DB 保存 → ナレッジ再読み込み
  """
  if not file.filename:
    raise HTTPException(status_code=400, detail="ファイル名がありません。")

  original_name = _safe_filename(file.filename)
  ext = Path(original_name).suffix.lower()

  if ext not in ALLOWED_EXT:
    raise HTTPException(
      status_code=400,
      detail=f"未対応形式です: {ext}（対応: {', '.join(sorted(ALLOWED_EXT))}）",
    )

  raw = await file.read()
  if not raw:
    raise HTTPException(status_code=400, detail="空ファイルはアップロードできません。")
  if len(raw) > 2 * 1024 * 1024:
    raise HTTPException(status_code=400, detail="ファイルが大きすぎます（上限2MB）。")

  # テキストに変換（UTF-8 基本、失敗したら errors='ignore'）
  try:
    text = raw.decode("utf-8")
  except UnicodeDecodeError:
    text = raw.decode("utf-8", errors="ignore")

  doc = KnowledgeDoc(
    original_name=original_name,
    stored_name=None,  # 物理ファイルは保存しない
    size=len(raw),
    content_type=file.content_type or "text/plain",
    content=text,
    status="active",
    created_at=datetime.utcnow(),
  )
  db.add(doc)
  db.commit()
  db.refresh(doc)

  reload_knowledge_cache(db=db)

  return {
    "ok": True,
    "id": doc.id,
    "original_name": doc.original_name,
  }


@router.delete("/{doc_id}", status_code=200)
def delete_doc(
  doc_id: int,
  _: dict = Depends(require_admin),
  db: Session = Depends(get_db),
):
  """
  文書削除 → DB から削除 → ナレッジ再読み込み
  """
  doc: Optional[KnowledgeDoc] = (
    db.query(KnowledgeDoc).filter(KnowledgeDoc.id == doc_id).first()
  )
  if not doc:
    raise HTTPException(status_code=404, detail="対象文書が見つかりません。")

  # 物理ファイルは使っていないので、DB 削除だけ
  db.delete(doc)
  db.commit()

  reload_knowledge_cache(db=db)

  return {"ok": True}


@router.post("/reload", status_code=200)
def reload_docs(_: dict = Depends(require_admin), db: Session = Depends(get_db)):
  """
  手動でナレッジ再読み込み
  """
  reload_knowledge_cache(db=db)
  return {"ok": True}
