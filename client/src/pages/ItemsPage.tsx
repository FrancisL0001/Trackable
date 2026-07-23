// Reusable list page for a subset of item kinds (Assignments / Tasks / Events).
// Filtering happens at the API layer (kinds/search); pagination metadata makes
// truncation visible instead of silently capping.
import { useDeferredValue, useMemo, useState } from "react";
import { Icon } from "../components/Icon";
import { ItemList } from "../components/ItemCard";
import { ItemForm } from "../components/ItemForm";
import { QueryError } from "../components/ErrorPage";
import {
  EmptyState,
  PageHeader,
  PageSkeleton,
  SectionTitle,
  TruncationHint,
} from "../components/ui";
import { useItems, useItemMutations } from "../hooks/items";
import type { Item, ItemKind } from "../api/types";

interface ItemsPageProps {
  title: string;
  subtitle: string;
  kinds: ItemKind[];
  defaultKind: ItemKind;
  emptyHint: string;
}

export function ItemsPage({
  title,
  subtitle,
  kinds,
  defaultKind,
  emptyHint,
}: ItemsPageProps) {
  const [search, setSearch] = useState("");
  const deferredSearch = useDeferredValue(search.trim());
  const { data, isLoading, isError, error, refetch } = useItems({
    kinds: kinds.join(","),
    search: deferredSearch || undefined,
  });
  const { create, update, toggle, remove } = useItemMutations();
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Item | null>(null);
  const [showDone, setShowDone] = useState(false);

  const split = useMemo(() => {
    const all = data?.items ?? [];
    return {
      open: all.filter((i) => i.status !== "done"),
      done: all.filter((i) => i.status === "done"),
    };
  }, [data]);

  if (isLoading) return <PageSkeleton />;
  if (isError) return <QueryError error={error} onRetry={() => refetch()} />;

  const openForm = (item: Item | null) => {
    setEditing(item);
    setShowForm(true);
  };
  const closeForm = () => {
    setShowForm(false);
    setEditing(null);
  };

  const isEmpty = split.open.length === 0 && split.done.length === 0;
  const searching = deferredSearch.length > 0;

  return (
    <div>
      <PageHeader
        title={title}
        subtitle={subtitle}
        action={
          <button className="btn btn-primary" onClick={() => openForm(null)}>
            <Icon name="plus" size={18} /> New
          </button>
        }
      />

      <div className="relative mb-4 max-w-md">
        <Icon
          name="search"
          size={16}
          className="absolute left-3.5 top-1/2 -translate-y-1/2 text-content-faint pointer-events-none"
        />
        <input
          className="input !pl-10"
          type="search"
          placeholder={`Search ${title.toLowerCase()}…`}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          aria-label={`Search ${title}`}
        />
      </div>

      {isEmpty ? (
        <div className="card">
          {searching ? (
            <EmptyState
              icon="search"
              title="No matches"
              hint={`Nothing matches “${deferredSearch}”.`}
            />
          ) : (
            <EmptyState
              title="Nothing here yet"
              hint={emptyHint}
              action={
                <button className="btn btn-primary" onClick={() => openForm(null)}>
                  <Icon name="plus" size={18} /> Add one
                </button>
              }
            />
          )}
        </div>
      ) : (
        <>
          {split.open.length > 0 ? (
            <ItemList
              items={split.open}
              onToggle={(i) => toggle.mutate(i)}
              onEdit={openForm}
              onDelete={(i) => remove.mutate(i)}
            />
          ) : (
            <div className="card">
              <EmptyState icon="check" title="All done here!" hint="Nice work." />
            </div>
          )}

          {data && <TruncationHint shown={data.items.length} total={data.total} />}

          {split.done.length > 0 && (
            <>
              <button
                className="btn btn-ghost btn-sm mt-4"
                onClick={() => setShowDone((s) => !s)}
              >
                <Icon name={showDone ? "chevron-left" : "chevron-right"} size={14} />
                {showDone ? "Hide" : "Show"} completed ({split.done.length})
              </button>
              {showDone && (
                <>
                  <SectionTitle icon="check">Completed</SectionTitle>
                  <ItemList
                    items={split.done}
                    onToggle={(i) => toggle.mutate(i)}
                    onDelete={(i) => remove.mutate(i)}
                  />
                </>
              )}
            </>
          )}
        </>
      )}

      {showForm && (
        <ItemForm
          initial={editing}
          defaultKind={defaultKind}
          onClose={closeForm}
          onSubmit={(input) =>
            editing
              ? update.mutateAsync({ id: editing.id, input }).then(() => undefined)
              : create.mutateAsync(input).then(() => undefined)
          }
        />
      )}
    </div>
  );
}
