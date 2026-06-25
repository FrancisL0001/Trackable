// Month calendar view: items placed on their due dates, with prev/next navigation.
import { useMemo, useState } from "react";
import { Icon } from "../components/Icon";
import { CenterSpinner, ErrorState, PageHeader } from "../components/ui";
import { ItemList } from "../components/ItemCard";
import { EmptyState } from "../components/ui";
import { useItems, useItemMutations } from "../hooks/items";
import { parseDate } from "../utils/date";
import type { Item } from "../api/types";

const DOW = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

function monthMatrix(year: number, month: number): Date[] {
  const first = new Date(year, month, 1);
  const start = new Date(first);
  start.setDate(first.getDate() - first.getDay()); // back to Sunday
  return Array.from({ length: 42 }, (_, i) => {
    const d = new Date(start);
    d.setDate(start.getDate() + i);
    return d;
  });
}

function sameDay(a: Date, b: Date): boolean {
  return (
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  );
}

export function Calendar() {
  const { data, isLoading, isError } = useItems();
  const { toggle } = useItemMutations();
  const today = new Date();
  const [cursor, setCursor] = useState(new Date(today.getFullYear(), today.getMonth(), 1));
  const [selected, setSelected] = useState<Date | null>(today);

  const byDay = useMemo(() => {
    const map = new Map<string, Item[]>();
    for (const item of data ?? []) {
      const d = parseDate(item.due_at) ?? parseDate(item.start_at);
      if (!d) continue;
      const key = `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
      const list = map.get(key);
      if (list) list.push(item);
      else map.set(key, [item]);
    }
    return map;
  }, [data]);

  if (isLoading) return <CenterSpinner label="Loading calendar…" />;
  if (isError) return <ErrorState />;

  const cells = monthMatrix(cursor.getFullYear(), cursor.getMonth());
  const dayItems = (d: Date) =>
    byDay.get(`${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`) ?? [];
  const monthLabel = cursor.toLocaleDateString(undefined, {
    month: "long",
    year: "numeric",
  });
  const shift = (delta: number) =>
    setCursor(new Date(cursor.getFullYear(), cursor.getMonth() + delta, 1));

  const selectedItems = selected ? dayItems(selected) : [];

  return (
    <div>
      <PageHeader
        title="Calendar"
        subtitle="See your month at a glance."
        action={
          <div className="flex items-center gap-2">
            <button className="icon-btn !w-9 !h-9" onClick={() => shift(-1)} aria-label="Previous month">
              <Icon name="menu" size={16} />
            </button>
            <span className="font-semibold min-w-[140px] text-center">{monthLabel}</span>
            <button className="icon-btn !w-9 !h-9" onClick={() => shift(1)} aria-label="Next month">
              <Icon name="menu" size={16} />
            </button>
            <button className="btn btn-ghost btn-sm" onClick={() => { setCursor(new Date(today.getFullYear(), today.getMonth(), 1)); setSelected(today); }}>
              Today
            </button>
          </div>
        }
      />

      <div className="card p-3">
        <div className="grid grid-cols-7 gap-1.5">
          {DOW.map((d) => (
            <div key={d} className="text-center text-[0.7rem] font-bold text-content-faint uppercase pb-1">
              {d}
            </div>
          ))}
          {cells.map((d, i) => {
            const inMonth = d.getMonth() === cursor.getMonth();
            const items = dayItems(d);
            const isToday = sameDay(d, today);
            const isSel = selected && sameDay(d, selected);
            return (
              <button
                key={i}
                onClick={() => setSelected(d)}
                className={`min-h-[84px] text-left border rounded-sm p-1.5 text-[0.8rem] overflow-hidden transition-colors ${
                  inMonth ? "bg-surface" : "bg-bg opacity-55"
                } ${isToday ? "border-primary ring-1 ring-primary" : "border-border"} ${
                  isSel ? "outline outline-2 outline-primary" : ""
                }`}
              >
                <div className="font-bold mb-1">{d.getDate()}</div>
                {items.slice(0, 3).map((it) => {
                  const tone =
                    it.status === "done"
                      ? "bg-surface-2 text-content-faint line-through"
                      : it.kind === "exam" || it.kind === "deadline"
                      ? "bg-accent-soft text-accent"
                      : "bg-primary-soft text-primary-strong";
                  return (
                    <span
                      key={it.id}
                      className={`block px-1.5 py-0.5 rounded-md mb-0.5 truncate font-semibold ${tone}`}
                    >
                      {it.title}
                    </span>
                  );
                })}
                {items.length > 3 && (
                  <span className="text-content-faint">+{items.length - 3} more</span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {selected && (
        <>
          <h2 className="flex items-center gap-2 text-xs uppercase tracking-wider text-content-faint font-bold mt-6 mb-2.5">
            {selected.toLocaleDateString(undefined, {
              weekday: "long",
              month: "short",
              day: "numeric",
            })}
          </h2>
          {selectedItems.length > 0 ? (
            <ItemList items={selectedItems} onToggle={(i) => toggle.mutate(i)} />
          ) : (
            <div className="card">
              <EmptyState icon="calendar" title="Nothing scheduled" hint="Enjoy the free time." />
            </div>
          )}
        </>
      )}
    </div>
  );
}
