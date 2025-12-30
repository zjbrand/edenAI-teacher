// frontend/src/components/admin/AdminView.tsx
import React, { useEffect, useState } from "react";
import { fetchSystemStatus, fetchUsers, setUserActive, setUserRole, type AdminUser } from "../../api/admin";
import {
  apiKnowledgeList,
  apiKnowledgeUpload,
  apiKnowledgeDelete,
  apiKnowledgeReload,
  type KnowledgeDocItem,
} from "../../api/knowledge";

export type AdminTab = "knowledge" | "users" | "system";

interface AdminViewProps {
  token: string;
  adminTab: AdminTab;
  setAdminTab: (tab: AdminTab) => void;
}

const AdminView: React.FC<AdminViewProps> = ({ token, adminTab, setAdminTab }) => {
  // ===== system status =====
  const [status, setStatus] = useState<any>(null);
  const [statusErr, setStatusErr] = useState<string | null>(null);

  // ===== knowledge =====
  const [docs, setDocs] = useState<KnowledgeDocItem[]>([]);
  const [docsErr, setDocsErr] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // ===== users =====
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [usersErr, setUsersErr] = useState<string | null>(null);
  const [usersLoading, setUsersLoading] = useState(false);

  const loadDocs = async () => {
    setDocsErr(null);
    const items = await apiKnowledgeList(token);
    setDocs(items);
  };

  const loadUsers = async () => {
    setUsersErr(null);
    setUsersLoading(true);
    try {
      const list = await fetchUsers();
      setUsers(list);
    } catch (e: any) {
      setUsersErr(e.message || "読み込み失敗");
    } finally {
      setUsersLoading(false);
    }
  };

  const loadSystem = async () => {
    setStatusErr(null);
    try {
      const s = await fetchSystemStatus();
      setStatus(s);
    } catch (e: any) {
      setStatusErr(e.message || "読み込み失敗");
    }
  };

  useEffect(() => {
    // タブ切替時に必要なデータだけ取得
    if (adminTab === "system") loadSystem();
    if (adminTab === "knowledge") loadDocs().catch((e) => setDocsErr(e.message || "読み込み失敗"));
    if (adminTab === "users") loadUsers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [adminTab]);

  // ===== knowledge actions =====
  const onUpload = async () => {
    if (!selectedFile) return;
    try {
      setUploading(true);
      await apiKnowledgeUpload(token, selectedFile);
      setSelectedFile(null);
      await loadDocs();
    } catch (e: any) {
      setDocsErr(e.message || "アップロードに失敗しました。");
    } finally {
      setUploading(false);
    }
  };

  const onDeleteDoc = async (id: number) => {
    if (!confirm("この文書を削除しますか？")) return;
    try {
      await apiKnowledgeDelete(token, id);
      await loadDocs();
    } catch (e: any) {
      setDocsErr(e.message || "削除に失敗しました。");
    }
  };

  const onReload = async () => {
    try {
      await apiKnowledgeReload(token);
      alert("ナレッジを再読み込みしました。");
    } catch (e: any) {
      setDocsErr(e.message || "再読み込みに失敗しました。");
    }
  };

  const fmtSize = (n: number) => {
    if (n < 1024) return `${n} B`;
    if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
    return `${(n / 1024 / 1024).toFixed(1)} MB`;
  };

  // ===== users actions =====
  const onToggleRole = async (u: AdminUser) => {
    const next = u.role === "admin" ? "user" : "admin";
    const ok = confirm(`権限を「${next}」に変更しますか？`);
    if (!ok) return;

    try {
      await setUserRole(u.id, next);
      await loadUsers();
    } catch (e: any) {
      setUsersErr(e.message || "権限変更に失敗しました。");
    }
  };

  const onToggleActive = async (u: AdminUser) => {
    const next = !u.is_active;
    const ok = confirm(next ? "このユーザーを再開しますか？" : "このユーザーを停止しますか？");
    if (!ok) return;

    try {
      await setUserActive(u.id, next);
      await loadUsers();
    } catch (e: any) {
      setUsersErr(e.message || "更新に失敗しました。");
    }
  };

  return (
    <div className="admin-view">
      <div className="admin-header">
        <h2>管理画面</h2>
        <p>ナレッジ文書 / ユーザー / システム状態</p>
      </div>

      <div className="admin-tabs">
        <button className={`admin-tab ${adminTab === "knowledge" ? "active" : ""}`} onClick={() => setAdminTab("knowledge")}>
          📚 ナレッジ
        </button>
        <button className={`admin-tab ${adminTab === "users" ? "active" : ""}`} onClick={() => setAdminTab("users")}>
          👤 ユーザー
        </button>
        <button className={`admin-tab ${adminTab === "system" ? "active" : ""}`} onClick={() => setAdminTab("system")}>
          ⚙ システム
        </button>
      </div>

      {/* ===== knowledge ===== */}
      {adminTab === "knowledge" && (
        <div className="admin-knowledge">
          <div className="admin-card">
            <h3>文書アップロード</h3>
            <p style={{ fontSize: 13, opacity: 0.8 }}>
              アップロードされた文書は storage/knowledge_files に保存され、再読み込み後に会話へ反映されます。
            </p>

            <div className="upload-row">
              <input type="file" accept=".txt,.md,.markdown" onChange={(e) => setSelectedFile(e.target.files?.[0] || null)} />
              <button className="primary-btn" onClick={onUpload} disabled={!selectedFile || uploading}>
                {uploading ? "アップロード中..." : "アップロード"}
              </button>

              <button className="outline-btn" onClick={onReload} style={{ marginLeft: 8 }}>
                再読み込み
              </button>
            </div>

            {docsErr && (
              <div className="auth-error" style={{ marginTop: 8 }}>
                {docsErr}
              </div>
            )}
          </div>

          <div className="admin-card">
            <h3>アップロード文書一覧</h3>
            <table className="admin-table">
              <thead>
                <tr>
                  <th>ファイル名</th>
                  <th>サイズ</th>
                  <th>登録日時</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {docs.map((d) => (
                  <tr key={d.id}>
                    <td>{d.original_name}</td>
                    <td>{fmtSize(d.size)}</td>
                    <td>{d.created_at ? d.created_at.replace("T", " ").slice(0, 19) : "-"}</td>
                    <td>
                      <button className="link-btn danger" onClick={() => onDeleteDoc(d.id)}>
                        削除
                      </button>
                    </td>
                  </tr>
                ))}
                {docs.length === 0 && (
                  <tr>
                    <td colSpan={4} style={{ opacity: 0.7, padding: 12 }}>
                      まだ文書がありません。
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ===== users ===== */}
    {adminTab === "users" && (
      <div className="admin-card">
        <h3>ユーザー管理</h3>
        <p style={{ fontSize: 13, opacity: 0.8 }}>
          ユーザーの有効 / 停止、および管理者昇格を行います。
        </p>

        {usersErr && <div className="auth-error">{usersErr}</div>}
        {usersLoading && <p style={{ opacity: 0.7 }}>読み込み中...</p>}

        {!usersLoading && (
          <table className="admin-table" style={{ marginTop: 8 }}>
            <thead>
              <tr>
                <th>メール</th>
                <th>氏名</th>
                <th>権限</th>
                <th>状態</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => {
                const active = u.is_active;
                return (
                  <tr key={u.id} style={!active ? { opacity: 0.6 } : undefined}>
                    <td>{u.email}</td>
                    <td>{u.full_name || "-"}</td>
                    <td>{u.role}</td>
                    <td>{active ? "有効" : "停止中"}</td>
                    <td>
                      {/* 管理者昇格：有効ユーザーのみ */}
                      {active && u.role !== "admin" && (
                        <button
                          className="link-btn"
                          onClick={async () => {
                            if (!confirm("このユーザーを管理者にしますか？")) return;
                            await fetch(`/admin/users/${u.id}/make-admin`, { method: "POST" });
                            await loadUsers();
                          }}
                        >
                          管理者にする
                        </button>
                      )}

                      {/* 停止 / 再開 */}
                      <button
                        className="link-btn danger"
                        onClick={() => onToggleActive(u)}
                        style={{ marginLeft: 8 }}
                      >
                        {active ? "停止" : "再開"}
                      </button>
                    </td>
                  </tr>
                );
              })}

              {users.length === 0 && (
                <tr>
                  <td colSpan={5} style={{ opacity: 0.7, padding: 12 }}>
                    ユーザーがいません。
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    )}


      {/* ===== system ===== */}
        {adminTab === "system" && (
          <div className="admin-card">
            <h3>システム状態</h3>

            <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 12 }}>
              {/* 全体ステータス */}
              <div className="status-card">
                <div className="status-title">全体状態</div>
                <div
                  className={`status-value ${
                    status?.ok ? "status-ok" : "status-ng"
                  }`}
                >
                  {status?.ok ? "正常稼働中" : "異常あり"}
                </div>
              </div>

              {/* LLM */}
              <div className="status-card">
                <div className="status-title">LLM サービス</div>
                <div
                  className={`status-value ${
                    status?.services?.llm === "ok" ? "status-ok" : "status-ng"
                  }`}
                >
                  {status?.services?.llm === "ok" ? "稼働中" : "停止"}
                </div>
              </div>

              {/* Vector Store */}
              <div className="status-card">
                <div className="status-title">ナレッジ検索</div>
                <div
                  className={`status-value ${
                    status?.services?.vector_store === "ok"
                      ? "status-ok"
                      : "status-ng"
                  }`}
                >
                  {status?.services?.vector_store === "ok" ? "正常" : "異常"}
                </div>
              </div>
            </div>

            {/* 統計情報 */}
            <div className="admin-card" style={{ marginTop: 8 }}>
              <h4>システム統計</h4>
              <div style={{ fontSize: 13, opacity: 0.9 }}>
                <div>👤 ユーザー数：{status?.stats?.users ?? "-"}</div>
                <div>📚 ナレッジ文書数：{status?.stats?.knowledge_docs ?? "-"}</div>
              </div>
            </div>

            {/* 操作 */}
            <div style={{ marginTop: 12 }}>
              <button className="outline-btn" onClick={loadSystem}>
                🔄 状態を再取得
              </button>
            </div>

            {statusErr && (
              <div className="auth-error" style={{ marginTop: 8 }}>
                {statusErr}
              </div>
            )}
          </div>
        )}
    </div>
  );
};

export default AdminView;
