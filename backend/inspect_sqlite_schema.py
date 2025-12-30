# inspect_sqlite_schema.py
from sqlalchemy import create_engine, text, inspect

SQLITE_URL = "sqlite:///./eden_teacher.db"

engine = create_engine(SQLITE_URL)

def print_table_info(table_name: str):
    print(f"\n=== {table_name} ===")
    with engine.connect() as conn:
        result = conn.execute(text(f"PRAGMA table_info({table_name});"))
        # PRAGMA table_info 結果: cid, name, type, notnull, dflt_value, pk
        for row in result:
            cid, name, col_type, notnull, dflt, pk = row
            print(f"{cid}: {name} {col_type} NOTNULL={notnull} PK={pk}, DEFAULT={dflt}")

def main():
    insp = inspect(engine)
    print("Tables:", insp.get_table_names())

    # 你现在关心这两个表
    print_table_info("knowledge_docs")
    print_table_info("users")

if __name__ == "__main__":
    main()
