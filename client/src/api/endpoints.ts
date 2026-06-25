// Typed endpoint functions grouped by resource.
import { api } from "./client";
import type {
  AuthResponse,
  Connection,
  Dashboard,
  Item,
  ItemInput,
  ProviderType,
  ReminderBuckets,
  StudyTip,
  SyncSummary,
  User,
} from "./types";

export const authApi = {
  register: (body: { email: string; password: string; full_name?: string }) =>
    api.post<AuthResponse>("/api/auth/register", body, true),
  login: (body: { email: string; password: string }) =>
    api.post<AuthResponse>("/api/auth/login", body, true),
  me: () => api.get<User>("/api/auth/me"),
};

function toQuery(params: Record<string, string | undefined>): string {
  const entries = Object.entries(params).filter(([, v]) => v);
  if (!entries.length) return "";
  return "?" + entries.map(([k, v]) => `${k}=${encodeURIComponent(v!)}`).join("&");
}

export const itemsApi = {
  list: (filters: Record<string, string | undefined> = {}) =>
    api.get<Item[]>(`/api/items${toQuery(filters)}`),
  create: (body: ItemInput) => api.post<Item>("/api/items", body),
  update: (id: number, body: Partial<ItemInput>) =>
    api.patch<Item>(`/api/items/${id}`, body),
  complete: (id: number, completed: boolean) =>
    api.post<Item>(`/api/items/${id}/complete?completed=${completed}`),
  remove: (id: number) => api.del<void>(`/api/items/${id}`),
};

export const integrationsApi = {
  providers: () =>
    api.get<{ demo_mode: boolean; providers: ProviderType[] }>(
      "/api/integrations/providers"
    ),
  connections: () => api.get<Connection[]>("/api/integrations/connections"),
  connect: (body: { provider: ProviderType; secrets?: Record<string, string> }) =>
    api.post<Connection>("/api/integrations/connections", body),
  disconnect: (id: number) => api.del<void>(`/api/integrations/connections/${id}`),
  toggle: (id: number, active: boolean) =>
    api.post<Connection>(`/api/integrations/connections/${id}/active?active=${active}`),
  sync: () => api.post<SyncSummary>("/api/integrations/sync"),
};

export const dashboardApi = {
  dashboard: () => api.get<Dashboard>("/api/dashboard"),
  reminders: () => api.get<ReminderBuckets>("/api/reminders"),
  studyTips: () => api.get<StudyTip[]>("/api/study-tips"),
};
