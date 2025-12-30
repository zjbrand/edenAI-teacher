# create_tables_postgres.py

from app.db import Base, engine

# 这两行导入是为了让 model 注册到 Base.metadata 里
from app.models import user, knowledge  # noqa: F401

def main():
    print("在当前 DATABASE_URL 上创建表结构...")
    Base.metadata.create_all(bind=engine)
    print("完成。")

if __name__ == "__main__":
    main()
