// frontend/src/api/admin.ts
import { API_BASE } from "../lib/api";

function getToken(): string | null {
  return localStorage.getItem("eden_token");
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getToken();

  // JSON API 用のヘッダー（FormData時は呼び出し側で上書き想定）
  const headers: Record<string, string> = {
    ...(init?.headers as Record<string, string>),
  };

  // Content-Type は body が FormData の時に付けない
  const isFormData = typeof FormData !== "undefined" && init?.body instanceof FormData;
  if (!isFormData && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text}`);
  }

  // 204 など JSON なし対策
  const ct = res.headers.get("content-type") || "";
  if (!ct.includes("application/json")) {
    return (undefined as unknown) as T;
  }
  return (await res.json()) as T;
}

export type SystemStatus = {
  ok: boolean;
  services: Record<string, string>;
  stats?: {
    users?: number;
    knowledge_docs?: number;
  };
};

export type AdminUser = {
  id: number;
  email: string;
  full_name?: string | null;
  role: "user" | "admin";
  is_active: boolean;
  created_at?: string | null;
};

export function fetchSystemStatus() {
  return request<SystemStatus>("/admin/system/status");
}

export function fetchUsers() {
  return request<AdminUser[]>("/admin/users");
}

// 役割変更
export function setUserRole(userId: number, role: "user" | "admin") {
  return request<AdminUser>(`/admin/users/${userId}/role`, {
    method: "PATCH",
    body: JSON.stringify({ role }),
  });
}

// 有効/無効
export function setUserActive(userId: number, is_active: boolean) {
  return request<AdminUser>(`/admin/users/${userId}/active`, {
    method: "PATCH",
    body: JSON.stringify({ is_active }),
  });
}

export function makeUserAdmin(userId: number) {
  return request<{ ok: boolean }>(`/admin/users/${userId}/make-admin`, {
    method: "POST",
  });
}

