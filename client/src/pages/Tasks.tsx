import { ItemsPage } from "./ItemsPage";

export function Tasks() {
  return (
    <ItemsPage
      title="Tasks"
      subtitle="Personal to-dos and job applications."
      kinds={["task", "job"]}
      defaultKind="task"
      emptyHint="Add a task to start checking things off."
    />
  );
}
