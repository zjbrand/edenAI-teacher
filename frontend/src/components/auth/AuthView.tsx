import React from "react";

type LoginRole = "user" | "admin";

interface Props {
  authMode: "login" | "register";
  setAuthMode: (m: "login" | "register") => void;

  authEmail: string;
  setAuthEmail: (v: string) => void;

  authPassword: string;
  setAuthPassword: (v: string) => void;

  authName: string;
  setAuthName: (v: string) => void;

  authError: string | null;
  onSubmit: (e: React.FormEvent) => void;
}

const AuthView: React.FC<Props> = ({
  authMode,
  setAuthMode,
  authEmail,
  setAuthEmail,
  authPassword,
  setAuthPassword,
  authName,
  setAuthName,
  authError,
  onSubmit,
}) => {
  const [loginRole, setLoginRole] = React.useState<LoginRole>("user");
  const isAdmin = loginRole === "admin";

  // 新規登録用：パスワード確認
  const [confirmPassword, setConfirmPassword] = React.useState("");
  // フロント側バリデーションエラー（サーバーの authError とは別）
  const [localError, setLocalError] = React.useState<string | null>(null);

  // ロール/モード切替時に入力補助をリセット（最小限）
  React.useEffect(() => {
    setLocalError(null);
    if (authMode !== "register") setConfirmPassword("");
  }, [authMode]);

  const handleRoleChange = (role: LoginRole) => {
    // ロール切替：エラー表示をリセット
    setLocalError(null);

    if (role === "admin") {
      // 管理者：登録不可（ログインのみ）
      setLoginRole("admin");
      setAuthMode("login");
      setConfirmPassword("");
      return;
    }

    // 一般ユーザー
    setLoginRole("user");
  };

  const handleSubmit = (e: React.FormEvent) => {
    // フロント側で新規登録の最低限チェック
    setLocalError(null);

    if (!isAdmin && authMode === "register") {
      // 新規登録：パスワード一致チェック
      if (authPassword !== confirmPassword) {
        e.preventDefault();
        setLocalError("パスワードが一致しません。もう一度確認してください。");
        return;
      }
      // 任意：空文字防止（念のため）
      if (!authPassword || !confirmPassword) {
        e.preventDefault();
        setLocalError("パスワードを入力してください。");
        return;
      }
    }

    // 既存の処理（App 側）へ委譲
    onSubmit(e);
  };

  return (
    <div className="auth-view">
      <div className="auth-card">
        {/* ロール選択（カード式タグ） */}
        <div className="role-card-tabs">
          <button
            type="button"
            className={`role-card ${loginRole === "user" ? "active" : ""}`}
            onClick={() => handleRoleChange("user")}
          >
            <div className="role-card-title">一般ユーザー</div>
            <div className="role-card-sub">会話機能を利用</div>
          </button>

          <button
            type="button"
            className={`role-card ${loginRole === "admin" ? "active" : ""}`}
            onClick={() => handleRoleChange("admin")}
          >
            <div className="role-card-title">管理者</div>
            <div className="role-card-sub">管理画面を利用</div>
          </button>
        </div>

        <h2 className="auth-title">
          {isAdmin ? "管理者ログイン" : authMode === "login" ? "ログイン" : "新規登録"}
        </h2>

        {isAdmin ? (
          <p className="auth-hint">管理者アカウントは事前作成済み（登録不可）</p>
        ) : authMode === "login" ? (
          <p className="auth-hint">メールアドレスとパスワードでログインしてください</p>
        ) : (
          <p className="auth-hint">必要事項を入力してアカウントを作成してください</p>
        )}

        <form onSubmit={handleSubmit}>
          {/* 一般ユーザーの新規登録のみ氏名を表示 */}
          {!isAdmin && authMode === "register" && (
            <div className="form-group">
              <label>氏名</label>
              <input
                type="text"
                value={authName}
                onChange={(e) => setAuthName(e.target.value)}
                placeholder="例）山田 太郎"
                autoComplete="name"
              />
            </div>
          )}

          <div className="form-group">
            <label>メールアドレス</label>
            <input
              type="email"
              value={authEmail}
              onChange={(e) => setAuthEmail(e.target.value)}
              placeholder="you@example.com"
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label>パスワード</label>
            <input
              type="password"
              value={authPassword}
              onChange={(e) => setAuthPassword(e.target.value)}
              placeholder="********"
              autoComplete={authMode === "register" ? "new-password" : "current-password"}
            />
          </div>

          {/* 新規登録のみ：パスワード（確認） */}
          {!isAdmin && authMode === "register" && (
            <div className="form-group">
              <label>パスワード（確認）</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="********"
                autoComplete="new-password"
              />
            </div>
          )}

          <button type="submit" className="primary-btn full-width">
            {isAdmin ? "管理者としてログイン" : authMode === "login" ? "ログイン" : "登録"}
          </button>
        </form>

        {/* フロント側バリデーションエラー */}
        {localError && <div className="auth-error">{localError}</div>}

        {/* サーバー側エラー（従来通り） */}
        {authError && <div className="auth-error">{authError}</div>}

        {/* 管理者は登録不可なので切替リンクを出さない */}
        {!isAdmin && (
          <div className="auth-switch">
            {authMode === "login" ? (
              <button
                type="button"
                onClick={() => {
                  setLocalError(null);
                  setAuthMode("register");
                }}
              >
                新規登録
              </button>
            ) : (
              <button
                type="button"
                onClick={() => {
                  setLocalError(null);
                  setAuthMode("login");
                }}
              >
                ログインへ戻る
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AuthView;
