import React from "react";
import logo from "../../assets/logo.png";

import type { Theme, View } from "../../types";

type Props = {
  theme: Theme;
  toggleTheme: () => void;

  activeView: View;
  setActiveView: (v: View) => void;

  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;

  isLoggedIn: boolean;
  onLogout: () => void;

  // ✅ 管理者のみ管理画面を表示
  isAdmin: boolean;
};

const Sidebar: React.FC<Props> = ({
  theme,
  toggleTheme,
  activeView,
  setActiveView,
  sidebarOpen,
  setSidebarOpen,
  isLoggedIn,
  onLogout,
  isAdmin,
}) => {
  return (
    <aside
      className={`sidebar ${sidebarOpen ? "open" : ""}`}
      onClick={() => sidebarOpen && setSidebarOpen(false)}
    >
      {/* 内側クリックで閉じないようにする */}
      <div className="sidebar-inner" onClick={(e) => e.stopPropagation()}>
        {/* ヘッダー */}
        <div className="sidebar-header">
          <img src={logo} alt="Eden" className="sidebar-logo" />
          <div className="sidebar-title">
            <div className="sidebar-title-main">Eden AI</div>
            <div className="sidebar-title-sub">プログラミング教師</div>
          </div>
        </div>

        {/* ナビ */}
        <nav className="sidebar-nav">
          <button
            type="button"
            className={`nav-item ${activeView === "chat" ? "active" : ""}`}
            onClick={() => {
              setActiveView("chat");
              setSidebarOpen(false);
            }}
          >
            💬 会話
          </button>

          {/* 管理者のみ */}
          {isAdmin && (
            <button
              type="button"
              className={`nav-item ${activeView === "admin" ? "active" : ""}`}
              onClick={() => {
                setActiveView("admin");
                setSidebarOpen(false);
              }}
            >
              📊 管理画面
            </button>
          )}

          <button
            type="button"
            className={`nav-item ${activeView === "settings" ? "active" : ""}`}
            onClick={() => {
              setActiveView("settings");
              setSidebarOpen(false);
            }}
          >
            ⚙ 設定
          </button>
        </nav>

        {/* フッター */}
        <div className="sidebar-footer">
          <button type="button" className="outline-btn" onClick={toggleTheme}>
            {theme === "dark" ? "ライトへ切替" : "ダークへ切替"}
          </button>

          {/* 未ログイン時は表示しない（あなたの仕様通り） */}
          {isLoggedIn && (
            <button
              type="button"
              className="outline-btn danger"
              onClick={() => {
                onLogout();
                setSidebarOpen(false);
              }}
            >
              ログアウト
            </button>
          )}
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
