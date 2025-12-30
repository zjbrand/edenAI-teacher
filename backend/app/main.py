from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ask import router as ask_router
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.api.admin_knowledge import router as admin_knowledge_router
from app.api.admin_users import router as admin_users_router
from app.api.admin_system import router as admin_system_router

from app.db import Base, engine, get_db
from app.models.user import User              # noqa: F401  モデル登録用
from app.models.knowledge import KnowledgeDoc  # noqa: F401  モデル登録用
from app.services.knowledge_service import reload_knowledge_cache

app = FastAPI(title="AI Teacher API (DeepSeek)")

# ===== CORS 设置 =====
# 本地开发 + 以后部署后的前端域名
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://edenai-teacher-2.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # 如果想暂时完全放开，可以改成 ["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== ルーター登録 =====
app.include_router(ask_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(admin_knowledge_router)
app.include_router(admin_users_router)
app.include_router(admin_system_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.on_event("startup")
def on_startup():
    """
    アプリ起動時に呼ばれる処理：
    - テーブル作成（存在しない場合）
    - ナレッジキャッシュの読み込み
    """
    # テーブル作成（SQLite/PostgreSQL どちらでも OK）
    Base.metadata.create_all(bind=engine)

    # ナレッジをロード
    with next(get_db()) as db:
        reload_knowledge_cache(db=db)
