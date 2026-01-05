# backend/tools/reset_knowledge_docs_table.py

from sqlalchemy import text

from app.db import engine, Base
from app.models.knowledge import KnowledgeDoc  # ← 如果你的文件/类名不同，这里改一下


def main() -> None:
    backend = engine.url.get_backend_name()
    print(f"Using DB backend: {backend}")

    # 先删表
    with engine.connect() as conn:
        if backend == "postgresql":
            # Postgres 支持 CASCADE
            conn.execute(text("DROP TABLE IF EXISTS knowledge_docs CASCADE;"))
        else:
            # SQLite 不支持 CASCADE 写法
            conn.execute(text("DROP TABLE IF EXISTS knowledge_docs;"))
        conn.commit()
        print("Dropped table knowledge_docs")

    # 再按 SQLAlchemy 模型重建表结构（带自增 id）
    Base.metadata.create_all(bind=engine, tables=[KnowledgeDoc.__table__])
    print("Recreated table knowledge_docs")


if __name__ == "__main__":
    main()
