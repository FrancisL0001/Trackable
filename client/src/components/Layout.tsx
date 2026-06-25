// Responsive app shell: desktop sidebar, mobile top bar + bottom nav.
import { NavLink, Outlet } from "react-router-dom";
import { Icon } from "./Icon";
import { NAV_ITEMS } from "./nav";
import { useAuth } from "../auth/AuthContext";
import { useTheme } from "../theme/ThemeContext";

function Brand() {
  return (
    <div className="flex items-center gap-2.5 font-extrabold text-xl px-2.5 pt-1.5 pb-4 tracking-tight">
      <span className="grid place-items-center w-8 h-8 rounded-[9px] bg-primary text-white">
        <Icon name="check" size={20} />
      </span>
      Trackable
    </div>
  );
}

function ThemeToggle() {
  const { theme, toggle } = useTheme();
  return (
    <button
      className="icon-btn"
      onClick={toggle}
      aria-label={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
    >
      <Icon name={theme === "light" ? "moon" : "sun"} />
    </button>
  );
}

export function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-screen">
      {/* Desktop sidebar */}
      <aside className="hidden md:flex w-[248px] shrink-0 flex-col gap-1 bg-bg-elevated border-r border-border p-5 sticky top-0 h-screen">
        <Brand />
        <nav className="flex flex-col gap-1">
          {NAV_ITEMS.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.to === "/"} className="nav-link">
              <Icon name={item.icon} size={18} />
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="mt-auto flex flex-col gap-1 border-t border-border pt-3">
          <div className="px-2.5 py-2 text-sm">
            <div className="font-semibold truncate">{user?.full_name || "Student"}</div>
            <div className="text-content-muted truncate text-[0.8rem]">{user?.email}</div>
          </div>
          <div className="flex gap-2">
            <ThemeToggle />
            <button className="btn btn-ghost flex-1" onClick={logout}>
              <Icon name="logout" size={18} /> Log out
            </button>
          </div>
        </div>
      </aside>

      <div className="flex-1 min-w-0 flex flex-col">
        {/* Mobile top bar */}
        <header className="md:hidden flex items-center justify-between px-4 py-3 border-b border-border bg-bg-elevated sticky top-0 z-20">
          <Brand />
          <div className="flex gap-2">
            <ThemeToggle />
            <button className="icon-btn" onClick={logout} aria-label="Log out">
              <Icon name="logout" />
            </button>
          </div>
        </header>

        <main className="px-4 md:px-8 pt-5 md:pt-7 pb-28 w-full max-w-app mx-auto">
          <Outlet />
        </main>
      </div>

      {/* Mobile bottom nav */}
      <nav className="md:hidden fixed bottom-0 inset-x-0 z-40 flex justify-around bg-bg-elevated border-t border-border px-1 py-1.5">
        {NAV_ITEMS.filter((i) => i.mobile).map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              `flex-1 flex flex-col items-center gap-0.5 px-0.5 py-1.5 text-[0.68rem] font-semibold rounded-lg no-underline ${
                isActive ? "text-primary" : "text-content-faint"
              }`
            }
          >
            <Icon name={item.icon} size={20} />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
