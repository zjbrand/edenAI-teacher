# backend/app/services/knowledge_service.py
# ナレッジ読み込み＆簡易検索（DB + 静的ファイル）

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.knowledge import KnowledgeDoc

# メモリ上のシンプルなキャッシュ（行単位）
_KNOWLEDGE_LINES: List[str] = []

# 静的ドキュメント（リポジトリに含まれている会社紹介など）
DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "company_docs"

SUPPORTED = {".txt", ".md", ".markdown"}


def _read_text_file(p: Path) -> str:
    """テキストファイルをUTF-8で読み込む（失敗したら errors=ignore）"""
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return p.read_text(encoding="utf-8", errors="ignore")


def load_all_knowledge(db: Optional[Session] = None) -> List[str]:
    """
    ① app/data/company_docs 配下の静的テキスト
    ② knowledge_docs テーブルの content（status='active'）
    をすべて読み込んで、テキストのリストを返す
    """
    texts: List[str] = []

    # 1) 静的 docs
    if DATA_DIR.exists():
        for p in sorted(DATA_DIR.glob("*")):
            if p.is_file() and p.suffix.lower() in SUPPORTED:
                texts.append(_read_text_file(p))

    # 2) DB 管理のナレッジ
    if db is not None:
        docs = (
            db.query(KnowledgeDoc)
            .filter(KnowledgeDoc.status == "active")
            .all()
        )
        for d in docs:
            if d.content:
                texts.append(d.content)

    return texts


def reload_knowledge_cache(db: Optional[Session] = None) -> None:
    """
    DB / 静的ファイルの内容をまとめて読み込み、行単位でキャッシュ
    """
    global _KNOWLEDGE_LINES

    texts = load_all_knowledge(db=db)

    lines: List[str] = []
    for t in texts:
        # CRLF, LF 両方に対応
        for line in t.splitlines():
            s = line.strip()
            if s:
                lines.append(s)

    _KNOWLEDGE_LINES = lines
    print("[KnowledgeBase] sample lines:", _KNOWLEDGE_LINES[:20])

    print(f"[KnowledgeBase] 合計 {len(_KNOWLEDGE_LINES)} 行のナレッジを読み込みました。")


def _normalize_query(query: str) -> str:
    """
    日本語クエリ用の簡易正規化：
    - 全角/半角の「?」「？」「。」「、」などの記号・空白を削除
    - 文字だけを残す
    """
    q = query.strip()
    # 記号・空白をざっくり削る
    q = re.sub(r"[？\?！!。、．\.,\s・]", "", q)
    return q


def get_relevant_context(query: str, top_k: int = 10) -> str:
    """
    文字レベルの超シンプル類似検索（改良版）

    - クエリと各行を同じルールで正規化して比較
    - 「ヒットした文字数 ÷ 行の長さの平方根」でスコアを計算
      → 短い見出し（例：代表取締役）にボーナスがかかる
    - スコアの高い行だけでなく、その前後の行も一緒に返す
      → 『代表取締役』の次の行に「何 暁楽」があるケースに対応
    """
    if not _KNOWLEDGE_LINES:
        return ""

    q_norm = _normalize_query(query)
    if not q_norm:
        # クエリがほぼ空なら、とりあえず先頭から
        return "\n".join(_KNOWLEDGE_LINES[:top_k])

    # 重複を除いた文字リスト
    chars = list(dict.fromkeys(q_norm))

    scored_indices: List[tuple[float, int]] = []

    for idx, line in enumerate(_KNOWLEDGE_LINES):
        line_norm = _normalize_query(line)
        if not line_norm:
            continue

        # クエリに含まれる文字が、この行に何個含まれているか
        raw_score = sum(1 for c in chars if c in line_norm)
        if raw_score == 0:
            continue

        # 行が長すぎるときはペナルティ（短い見出しを優先させる）
        length = max(5, len(line_norm))
        score = raw_score / (length ** 0.5)

        scored_indices.append((score, idx))

    if not scored_indices:
        # 一つもヒットしなかった場合は先頭から
        return "\n".join(_KNOWLEDGE_LINES[:top_k])

    # スコア降順にソート
    scored_indices.sort(key=lambda x: x[0], reverse=True)

    picked_lines: List[str] = []
    used_idx: set[int] = set()

    for score, idx in scored_indices:
        if len(picked_lines) >= top_k:
            break

        # この行と、その前後の行も一緒に拾う
        for j in (idx - 1, idx, idx + 1):
            if 0 <= j < len(_KNOWLEDGE_LINES) and j not in used_idx:
                picked_lines.append(_KNOWLEDGE_LINES[j])
                used_idx.add(j)
                if len(picked_lines) >= top_k:
                    break

    return "\n".join(picked_lines)

