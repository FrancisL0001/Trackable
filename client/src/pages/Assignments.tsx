import { ItemsPage } from "./ItemsPage";

export function Assignments() {
  return (
    <ItemsPage
      title="Assignments"
      subtitle="Everything you need to turn in, in one place."
      kinds={["assignment", "exam", "deadline"]}
      defaultKind="assignment"
      emptyHint="Add an assignment or sync Canvas/Gradescope to fill this in."
    />
  );
}
