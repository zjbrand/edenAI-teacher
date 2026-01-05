# backend/tools/reset_users_table.py

from sqlalchemy import text
from app.db import engine, Base
from app.models.user import User


def main():
    # 打印一下当前连接的数据库，确认是 sqlite 还是 postgres
    print("Using DB:", engine.url)

    # 1) 删掉 users 表（兼容 SQLite / Postgres，去掉 CASCADE）
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS users;"))
        print("Dropped table: users")

    # 2) 只重建 users 表
    Base.metadata.create_all(bind=engine, tables=[User.__table__])
    print("Re-created table: users")


if __name__ == "__main__":
    main()
