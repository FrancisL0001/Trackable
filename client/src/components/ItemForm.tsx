// Create/edit form for an item, rendered inside a Modal.
import { useState, type FormEvent } from "react";
import { Modal } from "./Modal";
import { ALL_KINDS, ALL_PRIORITIES, KIND_META } from "./itemMeta";
import { fromDatetimeLocal, toDatetimeLocal } from "../utils/date";
import type { Item, ItemInput, ItemKind, ItemPriority } from "../api/types";

interface ItemFormProps {
  initial?: Item | null;
  defaultKind?: ItemKind;
  onSubmit: (input: ItemInput) => Promise<void>;
  onClose: () => void;
}

export function ItemForm({ initial, defaultKind, onSubmit, onClose }: ItemFormProps) {
  const [title, setTitle] = useState(initial?.title ?? "");
  const [kind, setKind] = useState<ItemKind>(initial?.kind ?? defaultKind ?? "task");
  const [priority, setPriority] = useState<ItemPriority>(
    initial?.priority ?? "medium"
  );
  const [course, setCourse] = useState(initial?.course ?? "");
  const [location, setLocation] = useState(initial?.location ?? "");
  const [dueAt, setDueAt] = useState(toDatetimeLocal(initial?.due_at ?? null));
  const [description, setDescription] = useState(initial?.description ?? "");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setError("Please enter a title.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await onSubmit({
        title: title.trim(),
        kind,
        priority,
        course: course.trim(),
        location: location.trim(),
        description: description.trim(),
        due_at: fromDatetimeLocal(dueAt),
      });
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
      setSaving(false);
    }
  };

  return (
    <Modal title={initial ? "Edit item" : "New item"} onClose={onClose}>
      <form onSubmit={handleSubmit}>
        {error && (
          <div className="notice notice-danger mb-4" role="alert">
            {error}
          </div>
        )}

        <div className="field">
          <label className="field-label" htmlFor="if-title">
            Title
          </label>
          <input
            id="if-title"
            className="input"
            value={title}
            autoFocus
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Finish problem set 4"
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="field">
            <label className="field-label" htmlFor="if-kind">
              Type
            </label>
            <select
              id="if-kind"
              className="select"
              value={kind}
              onChange={(e) => setKind(e.target.value as ItemKind)}
            >
              {ALL_KINDS.map((k) => (
                <option key={k} value={k}>
                  {KIND_META[k].label}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label className="field-label" htmlFor="if-priority">
              Priority
            </label>
            <select
              id="if-priority"
              className="select"
              value={priority}
              onChange={(e) => setPriority(e.target.value as ItemPriority)}
            >
              {ALL_PRIORITIES.map((p) => (
                <option key={p} value={p}>
                  {p[0].toUpperCase() + p.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="field">
            <label className="field-label" htmlFor="if-course">
              Course (optional)
            </label>
            <input
              id="if-course"
              className="input"
              value={course}
              onChange={(e) => setCourse(e.target.value)}
              placeholder="e.g. CS 200"
            />
          </div>
          <div className="field">
            <label className="field-label" htmlFor="if-due">
              Due date (optional)
            </label>
            <input
              id="if-due"
              type="datetime-local"
              className="input"
              value={dueAt}
              onChange={(e) => setDueAt(e.target.value)}
            />
          </div>
        </div>

        <div className="field">
          <label className="field-label" htmlFor="if-location">
            Location (optional)
          </label>
          <input
            id="if-location"
            className="input"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="e.g. Library, Room 204"
          />
        </div>

        <div className="field">
          <label className="field-label" htmlFor="if-desc">
            Notes (optional)
          </label>
          <textarea
            id="if-desc"
            className="textarea"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        <div className="flex justify-end gap-2.5 mt-2">
          <button type="button" className="btn btn-ghost" onClick={onClose}>
            Cancel
          </button>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? "Saving…" : initial ? "Save changes" : "Create item"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
