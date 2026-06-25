import { describe, expect, it } from "vitest";
import {
  dueUrgency,
  formatDate,
  fromDatetimeLocal,
  parseDate,
  relativeDue,
} from "./date";

const NOW = new Date("2026-06-25T12:00:00Z");

describe("date utils", () => {
  it("parses valid and invalid dates", () => {
    expect(parseDate(null)).toBeNull();
    expect(parseDate("not-a-date")).toBeNull();
    expect(parseDate("2026-06-25T12:00:00Z")).toBeInstanceOf(Date);
  });

  it("formats dates and handles missing values", () => {
    expect(formatDate(null)).toBe("No date");
    expect(formatDate("2026-06-25T12:00:00Z")).toMatch(/2026/);
  });

  it("describes relative due dates", () => {
    expect(relativeDue("2026-06-25T20:00:00Z", NOW)).toBe("Due today");
    expect(relativeDue("2026-06-26T20:00:00Z", NOW)).toBe("Due tomorrow");
    expect(relativeDue("2026-06-23T20:00:00Z", NOW)).toBe("2 days overdue");
    expect(relativeDue(null, NOW)).toBe("No due date");
  });

  it("classifies urgency buckets", () => {
    expect(dueUrgency("2026-06-20T12:00:00Z", NOW)).toBe("overdue");
    expect(dueUrgency("2026-06-25T20:00:00Z", NOW)).toBe("today");
    expect(dueUrgency("2026-06-28T20:00:00Z", NOW)).toBe("soon");
    expect(dueUrgency("2026-08-01T20:00:00Z", NOW)).toBe("later");
    expect(dueUrgency(null, NOW)).toBe("none");
  });

  it("round-trips datetime-local conversion", () => {
    expect(fromDatetimeLocal("")).toBeNull();
    const iso = fromDatetimeLocal("2026-06-25T14:30");
    expect(iso).not.toBeNull();
    expect(new Date(iso!).getMinutes()).toBe(30);
  });
});
