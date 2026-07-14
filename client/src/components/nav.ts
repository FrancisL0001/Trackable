// Navigation destinations shared by the sidebar and the mobile bottom nav.
import type { IconName } from "./Icon";

export interface NavItem {
  to: string;
  label: string;
  icon: IconName;
  // Show in the compact mobile bottom nav.
  mobile?: boolean;
}

export const NAV_ITEMS: NavItem[] = [
  { to: "/", label: "Dashboard", icon: "dashboard", mobile: true },
  { to: "/calendar", label: "Calendar", icon: "calendar", mobile: true },
  { to: "/assignments", label: "Assignments", icon: "assignment", mobile: true },
  { to: "/tasks", label: "Tasks", icon: "task", mobile: true },
  { to: "/events", label: "Events", icon: "event" },
  { to: "/study-tips", label: "Study tips", icon: "bulb" },
  { to: "/integrations", label: "Integrations", icon: "plug", mobile: true },
];
