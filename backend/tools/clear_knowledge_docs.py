import sqlite3

conn = sqlite3.connect("eden_teacher.db")
cur = conn.cursor()
cur.execute("DELETE FROM knowledge_docs")
conn.commit()
print("knowledge_docs を全削除しました。")
cur.close()
conn.close()
