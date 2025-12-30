import sqlite3
from app.db import engine  # 关键：拿到后端同一个 DB

db_path = engine.url.database  # 这就是后端正在用的 sqlite 文件路径
ADMIN_EMAIL = "admin@example.com"  # 改成你注册的邮箱

print("Using DB:", db_path)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 看看目前 users 里有哪些
cur.execute("SELECT id, email, role FROM users")
rows = cur.fetchall()
print("Before:", rows)

cur.execute("UPDATE users SET role='admin' WHERE email=?", (ADMIN_EMAIL,))
conn.commit()

cur.execute("SELECT id, email, role FROM users WHERE email=?", (ADMIN_EMAIL,))
print("After:", cur.fetchall())

cur.close()
conn.close()
