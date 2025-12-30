// frontend/src/api.ts

//const API_BASE = "http://127.0.0.1:8000"; // FastAPI 后端地址
const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";

// ====== 类型 ======
export type Role = "user" | "assistant";

export interface ChatMessage {
  role: Role;
  content: string;
}

export interface AskResponse {
  answer: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

// ====== Token 工具函数 ======
const TOKEN_KEY = "eden_ai_token";

export function saveToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function loadToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

// ====== 请求封装 ======
function buildHeaders(token?: string): HeadersInit {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

// 1) 登录
export async function apiLogin(
  email: string,
  password: string
): Promise<LoginResponse> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: buildHeaders(),
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `登录失败，HTTP ${res.status}`);
  }

  const data = (await res.json()) as LoginResponse;
  return data;
}

// 2) 注册
export async function apiRegister(
  email: string,
  password: string,
  fullName?: string
): Promise<void> {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: buildHeaders(),
    body: JSON.stringify({
      email,
      password,
      full_name: fullName ?? null,
    }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `注册失败，HTTP ${res.status}`);
  }

  // 注册成功，我们不关心返回体，只要 200/201 即可
}

// 3) 问问题（带历史和可选 token）
export async function apiAsk(
  question: string,
  subject: string,
  history: ChatMessage[],
  token?: string
): Promise<AskResponse> {
  const res = await fetch(`${API_BASE}/api/ask`, {
    method: "POST",
    headers: buildHeaders(token),
    body: JSON.stringify({
      question,
      subject,
      history,
    }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `提问失败，HTTP ${res.status}`);
  }

  const data = (await res.json()) as AskResponse;
  return data;
}
