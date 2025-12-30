import React from "react";
import type { Message, Theme } from "../../types";

type Props = {
  theme: Theme;
  toggleTheme: () => void;

  subject: string;
  setSubject: (v: string) => void;

  messages: Message[];
  question: string;
  setQuestion: (v: string) => void;

  loading: boolean;
  error: string | null;

  onSend: () => void;
  onKeyDown: React.KeyboardEventHandler<HTMLTextAreaElement>;
};

const ChatView: React.FC<Props> = ({
  theme,
  toggleTheme,
  subject,
  setSubject,
  messages,
  question,
  setQuestion,
  loading,
  error,
  onSend,
  onKeyDown,
}) => {
  return (
    <div className="chat-view">
      <div className="top-bar">
        <div className="top-bar-left">
          <div className="app-title-block">
            <div className="app-title-main">Eden AI プログラミング教師</div>
            <div className="app-title-sub">自然言語でプログラミングを学ぶ · 複数ターン対話対応</div>
          </div>
        </div>

        <div className="top-bar-right">
          <div className="subject-select">
            <span>科目：</span>
            <select value={subject} onChange={(e) => setSubject(e.target.value)}>
              <option value="编程">汎用プログラミング</option>
              <option value="Python">Python</option>
              <option value="Java">Java</option>
              <option value="前端">フロントエンド開発</option>
              <option value="算法">アルゴリズム / データ構造</option>
            </select>
          </div>

          <button className="theme-toggle" onClick={toggleTheme}>
            {theme === "dark" ? "🌙ダーク" : "☀ ライト"}
          </button>
        </div>
      </div>

      <div className="chat-body">
        {messages.length === 0 && (
          <div className="chat-empty-hint">
            👉 試しに質問してみてください：
            <br />
            「変数とは何か、日常の例えで説明して？」
            <br />
            「ある数が素数かどうか判定するPython関数を書いて？」
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`chat-message-row ${msg.role === "user" ? "align-right" : "align-left"}`}
          >
            <div
              className={`chat-message-bubble ${msg.role === "user" ? "user-bubble" : "assistant-bubble"}`}
            >
              {msg.content}
            </div>
          </div>
        ))}
      </div>

      {error && <div className="error-bar">{error}</div>}

      <div className="input-bar">
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="あなたのプログラミングに関する質問を入力してください。Shift+Enterで改行、Enterで送信"
        />
        <button onClick={onSend} disabled={loading || !question.trim()}>
          {loading ? "考え中…" : "送信"}
        </button>
      </div>

      <div className="copyright">
        本ソフトウェアの著作権はエデン株式会社に帰属します。
      </div>
    </div>
  );
};

export default ChatView;
