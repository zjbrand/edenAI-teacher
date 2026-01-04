// src/api/knowledge.ts
// 管理者向け：ナレッジ文書 API

import { API_BASE } from "../lib/api";

export type KnowledgeDocItem = {
  id: number;
  original_name: string;
  stored_name: string;
  size: number;
  content_type?: string | null;
  created_at?: string | null;
};

function authHeaders(token: string) {
  return { Authorization: `Bearer ${token}` };
}

export async function apiKnowledgeList(token: string): Promise<KnowledgeDocItem[]> {
  const res = await fetch(`${API_BASE}/admin/knowledge`, {
    headers: { ...authHeaders(token) },
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function apiKnowledgeUpload(token: string, file: File) {
  const fd = new FormData();
  fd.append("file", file);

  const res = await fetch(`${API_BASE}/admin/knowledge/upload`, {
    method: "POST",
    headers: { ...authHeaders(token) }, // multipart のとき Content-Type は付けない
    body: fd,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function apiKnowledgeDelete(token: string, docId: number) {
  const res = await fetch(`${API_BASE}/admin/knowledge/${docId}`, {
    method: "DELETE",
    headers: { ...authHeaders(token) },
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function apiKnowledgeReload(token: string) {
  const res = await fetch(`${API_BASE}/admin/knowledge/reload`, {
    method: "POST",
    headers: { ...authHeaders(token) },
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
