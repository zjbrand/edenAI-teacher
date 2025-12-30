export type Role = "user" | "assistant";

export interface Message {
  role: Role;
  content: string;
}

export interface AskResponse {
  answer: string;
}

export type View = "chat" | "admin" | "settings";
export type Theme = "dark" | "light";
export type AuthMode = "login" | "register";
