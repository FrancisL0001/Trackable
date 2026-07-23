// Month calendar view: items placed on their due dates, with prev/next navigation.
// Fetches only the visible month's window from the API (not the whole item list).
import { useMemo, useState } from "react";
import { Icon } from "../components/Icon";
import { QueryError } from "../components/ErrorPage";
import { EmptyState, PageHeader, PageSkeleton } from "../components/ui";
import { ItemList } from "../components/ItemCard";
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
  const today = new Date();
  const [cursor, setCursor] = useState(new Date(today.getFullYear(), today.getMonth(), 1));
  const [selected, setSelected] = useState<Date | null>(today);

  const cells = useMemo(
    () => monthMatrix(cursor.getFullYear(), cursor.getMonth()),
    [cursor]
  );

  // Query the API for just the visible 6-week window.
  const windowStart = new Date(cells[0]);
  const windowEnd = new Date(cells[41]);
  windowEnd.setHours(23, 59, 59, 999);
  const { data, isLoading, isError, error, refetch } = useItems({
    due_after: windowStart.toISOString(),
    due_before: windowEnd.toISOString(),
    limit: "500",
  });

  const { toggle } = useItemMutations();

  const byDay = useMemo(() => {
    const map = new Map<string, Item[]>();
    for (const item of data?.items ?? []) {
      const d = parseDate(item.due_at) ?? parseDate(item.start_at);
      if (!d) continue;
      const key = `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
      const list = map.get(key);
      if (list) list.push(item);
      else map.set(key, [item]);
    }
    return map;
  }, [data]);

  if (isLoading) return <PageSkeleton />;
  if (isError) return <QueryError error={error} onRetry={() => refetch()} />;

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
          <div className="flex items-center gap-1.5">
            <button
              className="icon-btn !w-9 !h-9"
              onClick={() => shift(-1)}
              aria-label="Previous month"
            >
              <Icon name="chevron-left" size={17} />
            </button>
            <span className="font-bold min-w-[132px] text-center text-[0.95rem]">
              {monthLabel}
            </span>
            <button
              className="icon-btn !w-9 !h-9"
              onClick={() => shift(1)}
              aria-label="Next month"
            >
              <Icon name="chevron-right" size={17} />
            </button>
            <button
              className="btn btn-ghost btn-sm ml-1"
              onClick={() => {
                setCursor(new Date(today.getFullYear(), today.getMonth(), 1));
                setSelected(today);
              }}
            >
              Today
            </button>
          </div>
        }
      />

      <div className="card p-2 md:p-3">
        <div className="grid grid-cols-7 gap-1 md:gap-1.5">
          {DOW.map((d) => (
            <div
              key={d}
              className="text-center text-[0.66rem] font-bold text-content-faint uppercase tracking-wider pb-1.5"
            >
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
                aria-label={`${d.toDateString()}, ${items.length} item${items.length === 1 ? "" : "s"}`}
                className={`min-h-[58px] md:min-h-[88px] text-left border rounded-sm p-1 md:p-1.5 text-[0.78rem] overflow-hidden cursor-pointer transition-[border-color,background-color,box-shadow] duration-150 ${
                  inMonth ? "bg-surface" : "bg-bg opacity-50"
                } ${
                  isSel
                    ? "border-primary ring-2 ring-[color-mix(in_srgb,var(--primary)_40%,transparent)]"
                    : isToday
                    ? "border-primary/60"
                    : "border-border hover:border-border-strong"
                }`}
              >
                <div
                  className={`font-bold mb-1 grid place-items-center w-6 h-6 rounded-full tabular-nums ${
                    isToday ? "bg-primary text-white" : ""
                  }`}
                >
                  {d.getDate()}
                </div>

                {/* Mobile: dots. Desktop: titled chips. */}
                <div className="flex gap-0.5 md:hidden flex-wrap">
                  {items.slice(0, 4).map((it) => (
                    <span
                      key={it.id}
                      className={`w-1.5 h-1.5 rounded-full ${
                        it.status === "done"
                          ? "bg-content-faint"
                          : it.kind === "exam" || it.kind === "deadline"
                          ? "bg-accent"
                          : "bg-primary"
                      }`}
                    />
                  ))}
                  {items.length > 4 && (
                    <span className="text-[0.6rem] text-content-faint leading-none">
                      +{items.length - 4}
                    </span>
                  )}
                </div>
                <div className="hidden md:block">
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
                    <span className="text-content-faint text-[0.72rem]">
                      +{items.length - 3} more
                    </span>
                  )}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {selected && (
        <>
          <h2 className="flex items-center gap-2 text-xs uppercase tracking-[0.08em] text-content-faint font-bold mt-7 mb-2.5">
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
              <EmptyState
                icon="calendar"
                title="Nothing scheduled"
                hint="Enjoy the free time."
              />
            </div>
          )}
        </>
      )}
    </div>
  );
}
