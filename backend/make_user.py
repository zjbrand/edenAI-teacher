# backend/make_user.py
# ユーザー登録がDBに入っているか確認するだけの一時スクリプト

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "eden_teacher.db"
TARGET_EMAIL = "xiaoliu@example.com"  # ←確認したいメールに変更

print(f"Using DB: {DB_PATH}")

conn = sqlite3.connect(str(DB_PATH))
cur = conn.cursor()

# テーブル存在確認
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
tbl = cur.fetchone()
if not tbl:
    print("ERROR: users テーブルが見つかりません")
    cur.close()
    conn.close()
    raise SystemExit(1)

# 全件（必要なら件数だけでもOK）
cur.execute("SELECT id, email, full_name, role, created_at FROM users ORDER BY id")
rows = cur.fetchall()
print(f"Total users: {len(rows)}")
for r in rows:
    print(r)

print("\n--- lookup by email ---")
cur.execute(
    "SELECT id, email, full_name, role, created_at FROM users WHERE email = ?",
    (TARGET_EMAIL,),
)
print(cur.fetchall())

cur.close()
conn.close()
