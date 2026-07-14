// A single item row: complete toggle, title, metadata, and edit/delete actions.
import { Icon } from "./Icon";
import { KIND_META, PRIORITY_BADGE } from "./itemMeta";
import { dueUrgency, relativeDue } from "../utils/date";
import { safeHref } from "../utils/url";
import type { Item } from "../api/types";

interface ItemCardProps {
  item: Item;
  onToggle: (item: Item) => void;
  onEdit?: (item: Item) => void;
  onDelete?: (item: Item) => void;
}

const DUE_CLASS: Record<string, string> = {
  overdue: "text-danger font-semibold",
  today: "text-accent font-semibold",
  soon: "text-warning font-semibold",
  later: "text-content-muted",
  none: "text-content-faint",
};

export function ItemCard({ item, onToggle, onEdit, onDelete }: ItemCardProps) {
  const done = item.status === "done";
  const kind = KIND_META[item.kind];
  const urgency = done ? "none" : dueUrgency(item.due_at);
  const href = safeHref(item.url);

  return (
    <div className="group flex gap-3.5 items-start px-4 py-3.5 transition-colors duration-200 hover:bg-[color-mix(in_srgb,var(--surface-2)_55%,transparent)]">
      <button
        className={`mt-0.5 shrink-0 w-6 h-6 rounded-[8px] border-2 grid place-items-center cursor-pointer transition-[background-color,border-color,color] duration-200 ${
          done
            ? "bg-primary border-primary text-white"
            : "bg-surface border-border-strong text-transparent hover:border-primary"
        }`}
        onClick={() => onToggle(item)}
        aria-label={done ? "Mark as not done" : "Mark as done"}
        aria-pressed={done}
      >
        <Icon name="check" size={14} strokeWidth={3} />
      </button>

      <div className="flex-1 min-w-0">
        <div
          className={`font-semibold break-words leading-snug ${
            done ? "line-through text-content-faint" : ""
          }`}
        >
          {href ? (
            <a
              href={href}
              target="_blank"
              rel="noreferrer"
              className="hover:text-primary-strong transition-colors duration-150"
            >
              {item.title}
            </a>
          ) : (
            item.title
          )}
        </div>

        <div className="flex flex-wrap gap-x-2.5 gap-y-1.5 items-center mt-1.5 text-[0.8rem] text-content-muted">
          <span className="inline-flex items-center gap-1 text-content-faint">
            <Icon name={kind.icon} size={13} /> {kind.label}
          </span>
          {item.course && <span className="badge badge-primary">{item.course}</span>}
          {!done && item.priority !== "low" && (
            <span className={PRIORITY_BADGE[item.priority]}>{item.priority}</span>
          )}
          <span className={DUE_CLASS[urgency]}>{relativeDue(item.due_at)}</span>
          {item.location && (
            <span className="inline-flex items-center gap-1">
              <Icon name="pin" size={13} /> {item.location}
            </span>
          )}
          {item.source !== "manual" && (
            <span className="badge inline-flex items-center gap-1">
              <Icon name="link" size={12} /> {item.source.replace("_", " ")}
            </span>
          )}
        </div>
      </div>

      <div className="flex gap-1 shrink-0 md:opacity-0 md:group-hover:opacity-100 md:group-focus-within:opacity-100 transition-opacity duration-150">
        {onEdit && (
          <button
            className="icon-btn !w-9 !h-9"
            onClick={() => onEdit(item)}
            aria-label="Edit item"
          >
            <Icon name="edit" size={16} />
          </button>
        )}
        {onDelete && (
          <button
            className="icon-btn !w-9 !h-9 hover:!text-danger hover:!border-danger"
            onClick={() => onDelete(item)}
            aria-label="Delete item"
          >
            <Icon name="trash" size={16} />
          </button>
        )}
      </div>
    </div>
  );
}

export function ItemList({
  items,
  onToggle,
  onEdit,
  onDelete,
}: {
  items: Item[];
  onToggle: (item: Item) => void;
  onEdit?: (item: Item) => void;
  onDelete?: (item: Item) => void;
}) {
  return (
    <div className="card divide-y divide-border overflow-hidden">
      {items.map((item) => (
        <ItemCard
          key={item.id}
          item={item}
          onToggle={onToggle}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
