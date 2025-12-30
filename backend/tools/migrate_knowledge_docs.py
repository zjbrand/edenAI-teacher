# backend/migrate_knowledge_docs.py
# SQLite の knowledge_docs に不足カラムを追加（データは保持）

import sqlite3

DB_PATH = "eden_teacher.db"

def has_column(cur, table: str, col: str) -> bool:
    cur.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in cur.fetchall()]
    return col in cols

def add_column(cur, table: str, ddl: str):
    cur.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    table = "knowledge_docs"
    # 既に存在する前提：なければここで気づける
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    if not cur.fetchone():
        print(f"Table not found: {table}")
        return

    # 追加したいカラム（SQLite は ADD COLUMN のみ対応）
    # Boolean は INTEGER で持つのが無難
    targets = [
        ("is_active", "is_active INTEGER NOT NULL DEFAULT 1"),
        ("status", "status TEXT NOT NULL DEFAULT 'ready'"),
        ("chunk_count", "chunk_count INTEGER NOT NULL DEFAULT 0"),
        ("error_message", "error_message TEXT"),
        ("updated_at", "updated_at TEXT"),
    ]

    for col, ddl in targets:
        if has_column(cur, table, col):
            print(f"Skip: {col} already exists")
        else:
            print(f"Add: {col}")
            add_column(cur, table, ddl)

    conn.commit()

    # 確認
    cur.execute(f"PRAGMA table_info({table})")
    print(cur.fetchall())

    cur.close()
    conn.close()
    print("Done.")

if __name__ == "__main__":
    main()
