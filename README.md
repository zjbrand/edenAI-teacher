# EdenAI Teacher

**EdenAI Teacher** は、  
学習者が質問を投げかけると AI がわかりやすく回答してくれる  
**AI学習アシスタント Web アプリケーション**です。

企業紹介・社内ナレッジ文書などを知識ベースとして登録し、  
自然言語で検索・回答できることを目的としています。

---

## 🌐 デモ環境

| 種別 | URL |
|------|----|
| フロントエンド | https://edenai-teacher-2.onrender.com |
| バックエンド API | https://edenai-teacher.onrender.com |

※ Render 上で稼働

---

## 🏗 アーキテクチャ

本プロジェクトは **フロントエンド／バックエンド分離構成** です。

### Frontend
- Vite + React + TypeScript
- UIレンダリング & API呼び出し
- JWT によるログイン対応
- Static Site として Render にデプロイ

### Backend
- FastAPI (Python)
- OpenAI/Groq 互換 LLM API を使用
- Chat履歴対応
- JWT認証機能
- PostgreSQL による永続化
- Render Web Service としてデプロイ

---

## 📚 ナレッジベース機能

以下をサポートしています：

✔ `TXT / MD` 文書を DB に保存  
✔ 行単位でキャッシュ  
✔ 質問文章を正規化  
✔ 関連行をスコアリング  
✔ 回答の前提コンテキストとして LLM に付与  

例：


→ DBの知識から


を抽出し回答します。

---

## 🧠 主な機能

### 👤 ユーザー管理
- 新規登録
- ログイン
- JWT認証

### 💬 チャット形式 Q&A
- 履歴付き
- 教科（subject）指定可能

### 📁 ナレッジ管理（管理者向け）
- 文書登録
- DB 保存
- 状態管理（active など）

---

## 🗄 データベース

現在使用：

- PostgreSQL（Render）
- SQLAlchemy ORM

主なテーブル

| テーブル | 用途 |
|--------|----|
| `users` | ユーザー管理 |
| `knowledge_docs` | ナレッジ文書 |

---

## 🛠 ローカル開発手順

### Backend

cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload


http://127.0.0.1:8000


---

### Frontend



cd frontend
npm install
npm run dev

デフォルト：

http://127.0.0.1:5173

yaml
コードをコピーする

---

## 🔐 環境変数

### Backend

| 変数名 | 説明 |
|------|----|
| `DATABASE_URL` | PostgreSQL URL |
| `GROQ_API_KEY` | LLM APIキー |

---

### Frontend

`frontend/.env.production`

VITE_API_BASE=https://edenai-teacher.onrender.com

yaml
コードをコピーする

---

## 🚀 デプロイ

### Backend（Render Web Service）

- Root: `backend`
- Build:
pip install -r requirements.txt

diff
コードをコピーする
- Start:
uvicorn app.main:app --host 0.0.0.0 --port 10000

yaml
コードをコピーする

---

### Frontend（Render Static Site）

- Root: `frontend`
- Build:
npm install && npm run build

yaml
コードをコピーする
- Publish: `dist`

---

## 🔄 ナレッジキャッシュ

起動時：

reload_knowledge_cache()

yaml
コードをコピーする

が自動実行されます。

- DB
- 静的ファイル

→ 両方ロード

---

## 📂 注意点

- `backend/tools/`
  - SQLite → PostgreSQL 移行ツール
  - 開発用スクリプト
  - 本番では未使用

---

## 🎯 目的と背景

- IT教材用 AI システムとして設計
- 日本語対応
- 少人数企業・教育向け
- ナレッジ検索機能強化

---

## 🧑‍💻 技術スタック

### Backend
- Python 3
- FastAPI
- SQLAlchemy
- JWT
- LLM API

### Frontend
- React
- Vite
- TypeScript
- Fetch API

### Infra
- Render
- PostgreSQL

---

## 🚧 今後の改善予定

- 管理画面UI改善
- ナレッジ検索精度向上
- ドキュメントアップロード強化
- マルチユーザー権限

---

## 📜 ライセンス

個人開発・学習目的  
※ 商用利用時は調整予定

---

## 🙏 作者

中国出身・日本在住  
ITエンジニア × AI学習者

学習しながら成長するアプリを目指しています 😊


