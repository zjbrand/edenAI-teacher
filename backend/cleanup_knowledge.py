import sqlite3

DB_PATH = "eden_teacher.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("Before:")
cur.execute("SELECT id, original_name, stored_name FROM knowledge_docs")
for row in cur.fetchall():
    print(row)

# ★ 全部删除，重建一遍（只影响知识库，不动 users 表）
cur.execute("DELETE FROM knowledge_docs")
conn.commit()

print("\nAfter:")
cur.execute("SELECT id, original_name, stored_name FROM knowledge_docs")
print(cur.fetchall())

cur.close()
conn.close()
print("\n[done] knowledge_docs テーブルをリセットしました")
