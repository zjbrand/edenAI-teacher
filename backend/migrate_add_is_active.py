import sqlite3

DB_PATH = "eden_teacher.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 既存列確認
cur.execute("PRAGMA table_info(users)")
cols = [r[1] for r in cur.fetchall()]

if "is_active" not in cols:
    # SQLite: 既存テーブルに列追加
    cur.execute("ALTER TABLE users ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1")
    conn.commit()
    print("✅ users.is_active を追加しました（default=1）")
else:
    print("ℹ️ users.is_active は既に存在します")

# 確認
cur.execute("SELECT id, email, role, is_active FROM users")
print(cur.fetchall())

cur.close()
conn.close()
