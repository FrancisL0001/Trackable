// React Query hooks for items: listing and mutations with cache invalidation.
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { itemsApi } from "../api/endpoints";
import type { Item, ItemInput } from "../api/types";
import { useToast } from "../components/Toast";

export const itemKeys = {
  all: ["items"] as const,
  list: (filters: Record<string, string | undefined>) =>
    ["items", filters] as const,
};

export function useItems(filters: Record<string, string | undefined> = {}) {
  return useQuery({
    queryKey: itemKeys.list(filters),
    queryFn: () => itemsApi.list(filters),
  });
}

/** Invalidate every items list and the dashboard after a mutation. */
function useInvalidate() {
  const qc = useQueryClient();
  return () => {
    qc.invalidateQueries({ queryKey: itemKeys.all });
    qc.invalidateQueries({ queryKey: ["dashboard"] });
  };
}

export function useItemMutations() {
  const invalidate = useInvalidate();
  const { notify } = useToast();

  const create = useMutation({
    mutationFn: (input: ItemInput) => itemsApi.create(input),
    onSuccess: () => {
      invalidate();
      notify("Item created");
    },
  });

  const update = useMutation({
    mutationFn: ({ id, input }: { id: number; input: Partial<ItemInput> }) =>
      itemsApi.update(id, input),
    onSuccess: () => {
      invalidate();
      notify("Item updated");
    },
  });

  const toggle = useMutation({
    mutationFn: (item: Item) =>
      itemsApi.complete(item.id, item.status !== "done"),
    onSuccess: () => invalidate(),
  });

  const remove = useMutation({
    mutationFn: (item: Item) => itemsApi.remove(item.id),
    onSuccess: () => {
      invalidate();
      notify("Item deleted");
    },
  });

  return { create, update, toggle, remove };
}
