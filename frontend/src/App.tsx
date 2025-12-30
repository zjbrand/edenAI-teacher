import React, { useEffect, useState } from "react";
import "./App.css";

import Sidebar from "./components/layout/Sidebar";
import ChatView from "./components/chat/ChatView";
import AuthView from "./components/auth/AuthView";
import AdminView, { type AdminTab } from "./components/admin/AdminView";
import SettingsView from "./components/settings/SettingsView";

import type { Message, View, Theme, AuthMode } from "./types";
import { apiAsk, apiLogin, apiRegister, apiMe } from "./lib/api";
import type { MeResponse } from "./lib/api";

/**
 * ログイン種別
 * - user: 一般ユーザー
 * - admin: 管理者
 */
export type LoginType = "user" | "admin";

const App: React.FC = () => {
  // ================= チャット関連 =================
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [subject, setSubject] = useState("プログラミング");
  const [error, setError] = useState<string | null>(null);

  // ================= UI / レイアウト =================
  const [activeView, setActiveView] = useState<View>("chat");
  const [theme, setTheme] = useState<Theme>("dark");
  const [adminTab, setAdminTab] = useState<AdminTab>("knowledge");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // ================= 認証関連 =================
  const [token, setToken] = useState<string | null>(() =>
    typeof window !== "undefined" ? localStorage.getItem("eden_token") : null
  );
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(() =>
    typeof window !== "undefined" ? !!localStorage.getItem("eden_token") : false
  );

  // 🔖 ログイン種別（タグで切替）
  const [loginType, setLoginType] = useState<LoginType>("user");

  const [authMode, setAuthMode] = useState<AuthMode>("login");
  const [authEmail, setAuthEmail] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [authName, setAuthName] = useState("");
  const [authError, setAuthError] = useState<string | null>(null);

  // ✅ ログインユーザー情報
  const [me, setMe] = useState<MeResponse | null>(null);
  const isAdmin = me?.role === "admin";

  // ================= テーマ切替 =================
  const toggleTheme = () => setTheme((p) => (p === "dark" ? "light" : "dark"));

  // ================= 初期化：token があれば /me を叩く =================
  useEffect(() => {
    if (!token) {
      setMe(null);
      return;
    }

    (async () => {
      try {
        const meData = await apiMe(token);
        setMe(meData);
      } catch {
        // token が古い / 不正ならログアウト扱い
        setMe(null);
        setIsLoggedIn(false);
        setToken(null);
        localStorage.removeItem("eden_token");
      }
    })();
  }, [token]);

  // ================= メッセージ送信 =================
  const handleSend = async () => {
    const trimmed = question.trim();
    if (!trimmed || loading) return;

    if (!token) {
      alert("ログインしてください。");
      return;
    }

    setError(null);
    const newMessages: Message[] = [...messages, { role: "user", content: trimmed }];
    setMessages(newMessages);
    setQuestion("");
    setLoading(true);

    try {
      const historyPayload = newMessages.map((m) => ({ role: m.role, content: m.content }));
      const data = await apiAsk({
        token,
        question: trimmed,
        subject,
        history: historyPayload,
      });
      setMessages((prev) => [...prev, { role: "assistant", content: data.answer }]);
    } catch (e: any) {
      setError(e.message || "リクエスト失敗");
    } finally {
      setLoading(false);
    }
  };

  // ================= ログイン / 登録 =================
  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);

    // 管理者は登録不可
    if (loginType === "admin" && authMode === "register") {
      setAuthError("管理者アカウントは登録できません。");
      return;
    }

    try {
      // 一般ユーザーのみ登録可能
      if (loginType === "user" && authMode === "register") {
        await apiRegister(authEmail, authPassword, authName || null);
      }

      // ログイン
      const accessToken = await apiLogin(authEmail, authPassword);
      setToken(accessToken);
      setIsLoggedIn(true);
      localStorage.setItem("eden_token", accessToken);

      // ✅ ログイン直後に /me を取得して role を確定
      const meData = await apiMe(accessToken);
      setMe(meData);

      // ログイン後の遷移
      if (loginType === "admin") {
        if (meData.role !== "admin") {
          setAuthError("管理者権限がありません。");
          localStorage.removeItem("eden_token");
          setIsLoggedIn(false);
          setToken(null);
          setMe(null);
          return;
        }
        setActiveView("admin");
        setAdminTab("system");
      } else {
        setActiveView("chat");
      }

      setSidebarOpen(false);
    } catch (err: any) {
      setAuthError(err.message || "認証失敗");
    }
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setToken(null);
    setMe(null);
    localStorage.removeItem("eden_token");

    setAuthMode("login");
    setLoginType("user");
    setActiveView("chat");
    setSidebarOpen(false);
    setMessages([]);
  };

  // ================= メイン描画 =================
  const renderMainContent = () => {
    if (!isLoggedIn) {
      return (
        <AuthView
          loginType={loginType}
          setLoginType={setLoginType}
          authMode={authMode}
          setAuthMode={setAuthMode}
          authEmail={authEmail}
          setAuthEmail={setAuthEmail}
          authPassword={authPassword}
          setAuthPassword={setAuthPassword}
          authName={authName}
          setAuthName={setAuthName}
          authError={authError}
          onSubmit={handleAuthSubmit}
        />
      );
    }

    // 管理者以外が admin を開こうとしたら chat に戻す
    if (activeView === "admin" && !isAdmin) {
      return (
        <ChatView
          theme={theme}
          toggleTheme={toggleTheme}
          subject={subject}
          setSubject={setSubject}
          messages={messages}
          question={question}
          setQuestion={setQuestion}
          loading={loading}
          error={error}
          onSend={handleSend}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
        />
      );
    }

    if (activeView === "admin") {
      return <AdminView token={token!} adminTab={adminTab} setAdminTab={setAdminTab} />;
    }

    // ✅ ここが今回のポイント：設定画面を表示する
    if (activeView === "settings") {
      // me がまだ取得できてない場合の保険
      const email = me?.email ?? "";
      const fullName = me?.full_name ?? null;
      const role = me?.role ?? "user";

      return (
        <SettingsView
          token={token ?? ""}
          email={email}
          fullName={fullName}
          role={role}
        />
      );
    }

    // chat
    return (
      <ChatView
        theme={theme}
        toggleTheme={toggleTheme}
        subject={subject}
        setSubject={setSubject}
        messages={messages}
        question={question}
        setQuestion={setQuestion}
        loading={loading}
        error={error}
        onSend={handleSend}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
          }
        }}
      />
    );
  };

  return (
    <div className={`app-root ${theme}`}>
      <div className="app-layout">
        <Sidebar
          theme={theme}
          toggleTheme={toggleTheme}
          activeView={activeView}
          setActiveView={(v) => {
            // 管理者以外は admin へ遷移させない
            if (v === "admin" && !isAdmin) return;
            setActiveView(v);
          }}
          sidebarOpen={sidebarOpen}
          setSidebarOpen={setSidebarOpen}
          isLoggedIn={isLoggedIn}
          onLogout={handleLogout}
          isAdmin={!!isAdmin}
        />

        <main className="main-panel">{renderMainContent()}</main>
      </div>
    </div>
  );
};

export default App;
