// Reusable list page for a subset of item kinds (Assignments / Tasks / Events).
import { useMemo, useState } from "react";
import { Icon } from "../components/Icon";
import { ItemList } from "../components/ItemCard";
import { ItemForm } from "../components/ItemForm";
import {
  CenterSpinner,
  EmptyState,
  ErrorState,
  PageHeader,
  SectionTitle,
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
  const { data, isLoading, isError } = useItems();
  const { create, update, toggle, remove } = useItemMutations();
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Item | null>(null);
  const [showDone, setShowDone] = useState(false);

  const filtered = useMemo(() => {
    const all = (data ?? []).filter((i) => kinds.includes(i.kind));
    const open = all.filter((i) => i.status !== "done");
    const done = all.filter((i) => i.status === "done");
    return { open, done };
  }, [data, kinds]);

  if (isLoading) return <CenterSpinner label="Loading…" />;
  if (isError) return <ErrorState />;

  const openForm = (item: Item | null) => {
    setEditing(item);
    setShowForm(true);
  };
  const closeForm = () => {
    setShowForm(false);
    setEditing(null);
  };

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

      {filtered.open.length === 0 && filtered.done.length === 0 ? (
        <div className="card">
          <EmptyState
            title="Nothing here yet"
            hint={emptyHint}
            action={
              <button className="btn btn-primary" onClick={() => openForm(null)}>
                <Icon name="plus" size={18} /> Add one
              </button>
            }
          />
        </div>
      ) : (
        <>
          {filtered.open.length > 0 ? (
            <ItemList
              items={filtered.open}
              onToggle={(i) => toggle.mutate(i)}
              onEdit={openForm}
              onDelete={(i) => remove.mutate(i)}
            />
          ) : (
            <div className="card">
              <EmptyState icon="check" title="All done here!" hint="Nice work." />
            </div>
          )}

          {filtered.done.length > 0 && (
            <>
              <button
                className="btn btn-ghost btn-sm mt-4"
                onClick={() => setShowDone((s) => !s)}
              >
                {showDone ? "Hide" : "Show"} completed ({filtered.done.length})
              </button>
              {showDone && (
                <>
                  <SectionTitle icon="check">Completed</SectionTitle>
                  <ItemList
                    items={filtered.done}
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
