import { describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ItemCard } from "./ItemCard";
import type { Item } from "../api/types";

function makeItem(overrides: Partial<Item> = {}): Item {
  return {
    id: 1,
    title: "Problem Set 4",
    description: "",
    kind: "assignment",
    status: "todo",
    priority: "high",
    course: "CS 200",
    location: "",
    url: "",
    start_at: null,
    due_at: "2026-06-25T20:00:00Z",
    completed_at: null,
    source: "canvas",
    external_id: "canvas-1",
    connection_id: 1,
    user_edited_fields: [],
    created_at: "2026-06-01T00:00:00Z",
    updated_at: "2026-06-01T00:00:00Z",
    ...overrides,
  };
}

describe("ItemCard", () => {
  it("renders title, course, and provider source", () => {
    render(<ItemCard item={makeItem()} onToggle={() => {}} />);
    expect(screen.getByText("Problem Set 4")).toBeInTheDocument();
    expect(screen.getByText("CS 200")).toBeInTheDocument();
    expect(screen.getByText(/canvas/i)).toBeInTheDocument();
  });

  it("calls onToggle when the checkbox is clicked", () => {
    const onToggle = vi.fn();
    render(<ItemCard item={makeItem()} onToggle={onToggle} />);
    fireEvent.click(screen.getByRole("button", { name: /mark as done/i }));
    expect(onToggle).toHaveBeenCalledOnce();
  });

  it("shows completed styling and aria-pressed when done", () => {
    render(<ItemCard item={makeItem({ status: "done" })} onToggle={() => {}} />);
    const btn = screen.getByRole("button", { name: /mark as not done/i });
    expect(btn).toHaveAttribute("aria-pressed", "true");
  });

  it("renders edit and delete actions when handlers are provided", () => {
    const onEdit = vi.fn();
    const onDelete = vi.fn();
    render(
      <ItemCard item={makeItem()} onToggle={() => {}} onEdit={onEdit} onDelete={onDelete} />
    );
    fireEvent.click(screen.getByRole("button", { name: /edit item/i }));
    fireEvent.click(screen.getByRole("button", { name: /delete item/i }));
    expect(onEdit).toHaveBeenCalledOnce();
    expect(onDelete).toHaveBeenCalledOnce();
  });
});
