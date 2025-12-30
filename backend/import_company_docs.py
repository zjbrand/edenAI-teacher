# import_company_docs.py

from pathlib import Path

from app.db import SessionLocal
from app.models.knowledge import KnowledgeDoc
from app.services.knowledge_service import DATA_DIR, SUPPORTED, _read_text_file


def main():
    db = SessionLocal()

    if not DATA_DIR.exists():
        print("DATA_DIR 不存在：", DATA_DIR)
        return

    print("DATA_DIR =", DATA_DIR)

    for p in sorted(DATA_DIR.glob("*")):
        if not p.is_file() or p.suffix.lower() not in SUPPORTED:
            continue

        # 按 original_name 防止重复导入
        exists = (
            db.query(KnowledgeDoc)
            .filter(KnowledgeDoc.original_name == p.name)
            .first()
        )
        if exists:
            print("已存在，跳过:", p.name)
            continue

        content = _read_text_file(p)

        mime = "text/plain"
        if p.suffix.lower() in {".md", ".markdown"}:
            mime = "text/markdown"

        doc = KnowledgeDoc(
            original_name=p.name,
            stored_name=p.name,          # 如果你之后不再从磁盘读，就先这么用
            size=p.stat().st_size,
            content_type=mime,
            content=content,
            status="active",
        )

        db.add(doc)
        print("已导入:", p.name)

    db.commit()
    db.close()
    print("导入完成！")


if __name__ == "__main__":
    main()
