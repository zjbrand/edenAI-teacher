// src/lib/api.ts
const API_BASE = "http://127.0.0.1:8000";

export async function apiRegister(email: string, password: string, fullName?: string | null) {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, full_name: fullName ?? null }),
  });
  if (!res.ok) throw new Error(`注册失败: ${await res.text()}`);
}

export async function apiLogin(email: string, password: string): Promise<string> {
  // ★ FastAPI 側が OAuth2PasswordRequestForm を期待している前提（username/password）
  // ★ username に email を入れて送る
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", password);

  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: body.toString(),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`ログイン失敗: ${text}`);
  }

  const data = await res.json();
  if (!data?.access_token) throw new Error("access_token が返ってきませんでした");
  return data.access_token as string;
}

export async function apiAsk(params: {
  token: string;
  question: string;
  subject: string;
  history: { role: string; content: string }[];
}) {
  const res = await fetch(`${API_BASE}/api/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${params.token}`,
    },
    body: JSON.stringify({
      question: params.question,
      subject: params.subject,
      history: params.history,
    }),
  });

  if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
  return (await res.json()) as { answer: string };
}

export type MeResponse = {
  id: number;
  email: string;
  full_name: string | null;
  role: "user" | "admin" | string;
};

// ログイン中ユーザー情報
export async function apiMe(token: string): Promise<MeResponse> {
  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// パスワード変更
export async function apiChangePassword(
  token: string,
  currentPassword: string,
  newPassword: string
): Promise<{ ok: boolean }> {
  const res = await fetch(`${API_BASE}/auth/change-password`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
    }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
