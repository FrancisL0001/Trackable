// Responsive app shell: desktop sidebar, mobile top bar + bottom nav.
import { NavLink, Outlet } from "react-router-dom";
import { Footer } from "./Footer";
import { Icon } from "./Icon";
import { NAV_ITEMS } from "./nav";
import { useAuth } from "../auth/AuthContext";
import { useTheme } from "../theme/ThemeContext";

export function Brand({ size = "md" }: { size?: "md" | "lg" }) {
  const box =
    size === "lg" ? "w-10 h-10 rounded-[12px]" : "w-8 h-8 rounded-[9px]";
  const text = size === "lg" ? "text-2xl" : "text-xl";
  return (
    <div
      className={`flex items-center gap-2.5 font-extrabold ${text} tracking-tight`}
    >
      <span
        className={`grid place-items-center ${box} brand-mark text-white shadow-sm`}
      >
        <Icon name="check" size={size === "lg" ? 22 : 18} />
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
      <Icon name={theme === "light" ? "moon" : "sun"} size={18} />
    </button>
  );
}

function UserCard() {
  const { user, logout } = useAuth();
  const initial = (user?.full_name || user?.email || "?")
    .trim()[0]
    ?.toUpperCase();
  return (
    <div className="mt-auto border-t border-border pt-3 flex flex-col gap-2">
      <div className="flex items-center gap-2.5 px-1.5 py-1.5 min-w-0">
        <span
          className="shrink-0 grid place-items-center w-9 h-9 rounded-full brand-mark text-white font-bold text-sm"
          aria-hidden="true"
        >
          {initial}
        </span>
        <div className="min-w-0 text-sm">
          <div className="font-semibold truncate">
            {user?.full_name || "Student"}
          </div>
          <div className="text-content-faint truncate text-[0.78rem]">
            {user?.email}
          </div>
        </div>
      </div>
      <div className="flex gap-2">
        <ThemeToggle />
        <button
          className="btn btn-ghost btn-sm flex-1 justify-start"
          onClick={logout}
        >
          <Icon name="logout" size={17} /> Log out
        </button>
      </div>
    </div>
  );
}

export function Layout() {
  const { logout } = useAuth();

  return (
    <div className="flex min-h-screen">
      {/* Desktop sidebar */}
      <aside className="hidden md:flex w-[250px] shrink-0 flex-col gap-1 bg-bg-elevated border-r border-border px-4 py-5 sticky top-0 h-screen">
        <div className="px-2 pt-1 pb-5">
          <Brand />
        </div>
        <nav className="flex flex-col gap-0.5" aria-label="Primary">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className="nav-link"
            >
              <Icon name={item.icon} size={18} />
              {item.label}
            </NavLink>
          ))}
        </nav>
        <UserCard />
      </aside>

      <div className="flex-1 min-w-0 flex flex-col">
        {/* Mobile top bar */}
        <header className="md:hidden flex items-center justify-between px-4 py-2.5 border-b border-border bg-[color-mix(in_srgb,var(--bg-elevated)_88%,transparent)] backdrop-blur-md sticky top-0 z-30">
          <Brand />
          <div className="flex gap-2">
            <ThemeToggle />
            <button className="icon-btn" onClick={logout} aria-label="Log out">
              <Icon name="logout" size={18} />
            </button>
          </div>
        </header>

        <main className="px-4 md:px-8 pt-5 md:pt-7 pb-32 md:pb-12 w-full max-w-app mx-auto">
          <Outlet />
          <Footer />
        </main>
      </div>

      {/* Mobile bottom nav */}
      <nav
        className="md:hidden fixed bottom-0 inset-x-0 z-40 flex justify-around bg-[color-mix(in_srgb,var(--bg-elevated)_92%,transparent)] backdrop-blur-md border-t border-border px-1 pt-1.5"
        style={{ paddingBottom: "max(0.375rem, env(safe-area-inset-bottom))" }}
        aria-label="Primary"
      >
        {NAV_ITEMS.filter((i) => i.mobile).map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              `flex-1 flex flex-col items-center gap-1 px-0.5 py-1.5 text-[0.66rem] font-semibold rounded-lg no-underline transition-colors duration-200 ${
                isActive ? "text-primary-strong" : "text-content-faint"
              }`
            }
          >
            {({ isActive }) => (
              <>
                <span
                  className={`grid place-items-center w-11 h-6 rounded-full transition-colors duration-200 ${
                    isActive ? "bg-primary-soft" : ""
                  }`}
                >
                  <Icon name={item.icon} size={19} />
                </span>
                {item.label}
              </>
            )}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
