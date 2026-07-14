import { ItemsPage } from "./ItemsPage";

export function Events() {
  return (
    <ItemsPage
      title="Events & meetings"
      subtitle="Classes, meetings, and everything on your calendar."
      kinds={["event", "meeting"]}
      defaultKind="event"
      emptyHint="Add an event or connect Google Calendar."
    />
  );
}
