// Shared API types mirroring the backend Pydantic schemas.

export type ItemKind =
  | "assignment"
  | "event"
  | "meeting"
  | "task"
  | "job"
  | "exam"
  | "deadline";

export type ItemStatus = "todo" | "in_progress" | "done";
export type ItemPriority = "low" | "medium" | "high";
export type ProviderType =
  | "canvas"
  | "google_calendar"
  | "gradescope"
  | "ics"
  | "manual";

export interface User {
  id: number;
  email: string;
  full_name: string;
  timezone: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Item {
  id: number;
  title: string;
  description: string;
  kind: ItemKind;
  status: ItemStatus;
  priority: ItemPriority;
  course: string;
  location: string;
  url: string;
  start_at: string | null;
  due_at: string | null;
  completed_at: string | null;
  source: ProviderType;
  external_id: string;
  created_at: string;
  updated_at: string;
}

export interface ItemInput {
  title: string;
  description?: string;
  kind?: ItemKind;
  status?: ItemStatus;
  priority?: ItemPriority;
  course?: string;
  location?: string;
  url?: string;
  start_at?: string | null;
  due_at?: string | null;
}

export interface Connection {
  id: number;
  provider: ProviderType;
  is_active: boolean;
  display_name: string;
  last_synced_at: string | null;
  last_sync_status: string;
  created_at: string;
}

export interface SyncResult {
  provider: ProviderType;
  created: number;
  updated: number;
  total: number;
  status: string;
}

export interface SyncSummary {
  results: SyncResult[];
  total_created: number;
  total_updated: number;
}

export interface ReminderBuckets {
  overdue: Item[];
  today: Item[];
  soon: Item[];
  upcoming: Item[];
}

export interface DashboardStats {
  total_open: number;
  overdue: number;
  due_today: number;
  due_this_week: number;
  completed_this_week: number;
  by_course: Record<string, number>;
}

export interface Dashboard {
  stats: DashboardStats;
  reminders: ReminderBuckets;
  next_up: Item[];
}

export interface StudyTip {
  title: string;
  body: string;
  category: string;
}
