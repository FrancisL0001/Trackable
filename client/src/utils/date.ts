// Date formatting and relative-time helpers, all timezone-aware via the browser.

export function parseDate(value: string | null): Date | null {
  if (!value) return null;
  const d = new Date(value);
  return isNaN(d.getTime()) ? null : d;
}

export function formatDate(value: string | null): string {
  const d = parseDate(value);
  if (!d) return "No date";
  return d.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function formatDateTime(value: string | null): string {
  const d = parseDate(value);
  if (!d) return "No date";
  return d.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function formatTime(value: string | null): string {
  const d = parseDate(value);
  if (!d) return "";
  return d.toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" });
}

const DAY = 86_400_000;

/** Human relative description like "2 days overdue" / "Due today" / "in 3 days". */
export function relativeDue(value: string | null, now: Date = new Date()): string {
  const d = parseDate(value);
  if (!d) return "No due date";
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const startOfDue = new Date(d.getFullYear(), d.getMonth(), d.getDate());
  const dayDiff = Math.round((startOfDue.getTime() - startOfToday.getTime()) / DAY);

  if (dayDiff === 0) return "Due today";
  if (dayDiff === 1) return "Due tomorrow";
  if (dayDiff === -1) return "1 day overdue";
  if (dayDiff < 0) return `${Math.abs(dayDiff)} days overdue`;
  if (dayDiff < 7) return `Due in ${dayDiff} days`;
  return `Due ${formatDate(value)}`;
}

export type DueUrgency = "overdue" | "today" | "soon" | "later" | "none";

export function dueUrgency(value: string | null, now: Date = new Date()): DueUrgency {
  const d = parseDate(value);
  if (!d) return "none";
  if (d.getTime() < now.getTime()) return "overdue";
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const startOfDue = new Date(d.getFullYear(), d.getMonth(), d.getDate());
  const dayDiff = Math.round((startOfDue.getTime() - startOfToday.getTime()) / DAY);
  if (dayDiff === 0) return "today";
  if (dayDiff <= 7) return "soon";
  return "later";
}

/** Format value for a datetime-local input (local time, no seconds). */
export function toDatetimeLocal(value: string | null): string {
  const d = parseDate(value);
  if (!d) return "";
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(
    d.getHours()
  )}:${pad(d.getMinutes())}`;
}

/** Convert a datetime-local input value to an ISO string (or null). */
export function fromDatetimeLocal(value: string): string | null {
  if (!value) return null;
  const d = new Date(value);
  return isNaN(d.getTime()) ? null : d.toISOString();
}
