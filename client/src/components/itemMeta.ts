// Display metadata for item kinds, priorities, and providers.
import type { IconName } from "./Icon";
import type { ItemKind, ItemPriority, ProviderType } from "../api/types";

export const KIND_META: Record<ItemKind, { label: string; icon: IconName }> = {
  assignment: { label: "Assignment", icon: "assignment" },
  event: { label: "Event", icon: "calendar" },
  meeting: { label: "Meeting", icon: "event" },
  task: { label: "Task", icon: "task" },
  job: { label: "Job", icon: "job" },
  exam: { label: "Exam", icon: "alert" },
  deadline: { label: "Deadline", icon: "clock" },
};

export const PRIORITY_BADGE: Record<ItemPriority, string> = {
  low: "badge",
  medium: "badge badge-warning",
  high: "badge badge-danger",
};

// Fallback display metadata; the Integrations page prefers the server's
// capability metadata (label/description/live_supported) when available.
export const PROVIDER_META: Record<
  ProviderType,
  { label: string; description: string; monogram: string; tone: string }
> = {
  canvas: {
    label: "Canvas",
    description: "Sync assignments and due dates from your Canvas courses.",
    monogram: "C",
    tone: "bg-danger-soft text-danger",
  },
  google_calendar: {
    label: "Google Calendar (iCal feed)",
    description: "Pull in events and meetings via your calendar's secret iCal URL.",
    monogram: "G",
    tone: "bg-primary-soft text-primary-strong",
  },
  gradescope: {
    label: "Gradescope",
    description: "Preview Gradescope homework and submission deadlines.",
    monogram: "Gs",
    tone: "bg-success-soft text-success",
  },
  ics: {
    label: "Course feed (ICS)",
    description: "Import any calendar feed from a course website or portal.",
    monogram: "iC",
    tone: "bg-accent-soft text-accent",
  },
  web_page: {
    label: "Course website (AI import)",
    description: "Extract deadlines from an assignments page with no feed.",
    monogram: "Ai",
    tone: "bg-warning-soft text-warning",
  },
  manual: {
    label: "Manual",
    description: "Items you create yourself.",
    monogram: "M",
    tone: "bg-surface-2 text-content-muted",
  },
};

export const ALL_KINDS: ItemKind[] = [
  "task",
  "assignment",
  "exam",
  "deadline",
  "event",
  "meeting",
  "job",
];

export const ALL_PRIORITIES: ItemPriority[] = ["low", "medium", "high"];
