# migrate_sqlite_to_postgres.py

import os
from sqlalchemy import create_engine, MetaData, Table, select, text

# 1) 本地 SQLite
SQLITE_URL = "sqlite:///./eden_teacher.db"

# 2) Render 的 External Database URL，优先从环境变量 POSTGRES_URL 读
POSTGRES_URL = os.getenv("POSTGRES_URL")
if not POSTGRES_URL:
    raise RuntimeError("请先在环境变量 POSTGRES_URL 中设置 Postgres 连接字符串 (External Database URL)")

# 转成 SQLAlchemy 认可的格式
if POSTGRES_URL.startswith("postgres://"):
    POSTGRES_URL = POSTGRES_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif POSTGRES_URL.startswith("postgresql://"):
    # SQLAlchemy 需要 postgresql+psycopg2://
    POSTGRES_URL = POSTGRES_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

print("使用的 Postgres URL:", POSTGRES_URL)

# 创建两个 engine
sqlite_engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
pg_engine = create_engine(POSTGRES_URL)

# 反射 SQLite 的表结构（只需要反射 SQLite，Postgres 我们自己建表）
sqlite_meta = MetaData()
sqlite_meta.reflect(bind=sqlite_engine, only=["users", "knowledge_docs"])

sqlite_users = Table("users", sqlite_meta, autoload_with=sqlite_engine)
sqlite_knowledge = Table("knowledge_docs", sqlite_meta, autoload_with=sqlite_engine)


def create_tables_in_postgres():
    """在 Postgres 中手动建 users 和 knowledge_docs 表（如果不存在）"""
    create_users_sql = text("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        email VARCHAR NOT NULL,
        hashed_password VARCHAR NOT NULL,
        full_name VARCHAR,
        created_at TIMESTAMP,
        role VARCHAR NOT NULL,
        is_active BOOLEAN NOT NULL
    );
    """)

    create_knowledge_sql = text("""
    CREATE TABLE IF NOT EXISTS knowledge_docs (
        id INTEGER PRIMARY KEY,
        original_name VARCHAR NOT NULL,
        stored_name VARCHAR,
        size INTEGER NOT NULL,
        content_type VARCHAR,
        content TEXT NOT NULL,
        status VARCHAR NOT NULL,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    );
    """)

    with pg_engine.begin() as conn:
        conn.execute(create_users_sql)
        conn.execute(create_knowledge_sql)
        print("Postgres 中已确保存在 users / knowledge_docs 表。")


def migrate():
    # 1) 先在 Postgres 建表
    create_tables_in_postgres()

    # 2) 迁移数据
    with sqlite_engine.connect() as s_conn, pg_engine.begin() as p_conn:
        # ---- users ----
        users_rows = s_conn.execute(select(sqlite_users)).mappings().all()
        print(f"即将迁移 users 表 {len(users_rows)} 行")

        # 先清空 Postgres 里的 users，避免重复插入（按需，你也可以去掉这一句）
        p_conn.execute(text("DELETE FROM users;"))

        for row in users_rows:
            data = {
                "id": row["id"],
                "email": row["email"],
                "hashed_password": row["hashed_password"],
                "full_name": row["full_name"],
                "created_at": row["created_at"],
                "role": row["role"],
                "is_active": row["is_active"],
            }
            p_conn.execute(text("""
                INSERT INTO users (id, email, hashed_password, full_name, created_at, role, is_active)
                VALUES (:id, :email, :hashed_password, :full_name, :created_at, :role, :is_active)
            """), data)

        # ---- knowledge_docs ----
        docs_rows = s_conn.execute(select(sqlite_knowledge)).mappings().all()
        print(f"即将迁移 knowledge_docs 表 {len(docs_rows)} 行")

        p_conn.execute(text("DELETE FROM knowledge_docs;"))

        for row in docs_rows:
            data = {
                "id": row["id"],
                "original_name": row["original_name"],
                "stored_name": row["stored_name"],
                "size": row["size"],
                "content_type": row["content_type"],
                "content": row["content"],
                "status": row["status"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
            p_conn.execute(text("""
                INSERT INTO knowledge_docs (
                    id, original_name, stored_name, size,
                    content_type, content, status,
                    created_at, updated_at
                )
                VALUES (
                    :id, :original_name, :stored_name, :size,
                    :content_type, :content, :status,
                    :created_at, :updated_at
                )
            """), data)

    print("迁移完成！")


if __name__ == "__main__":
    migrate()
