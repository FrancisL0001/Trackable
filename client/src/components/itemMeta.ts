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

export const PROVIDER_META: Record<
  ProviderType,
  { label: string; description: string }
> = {
  canvas: {
    label: "Canvas",
    description: "Sync assignments and due dates from your Canvas courses.",
  },
  google_calendar: {
    label: "Google Calendar",
    description: "Pull in events and meetings from your calendar.",
  },
  gradescope: {
    label: "Gradescope",
    description: "Track Gradescope homework and submission deadlines.",
  },
  ics: {
    label: "Course website (ICS)",
    description: "Import any calendar feed from a course website or portal.",
  },
  manual: { label: "Manual", description: "Items you create yourself." },
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
