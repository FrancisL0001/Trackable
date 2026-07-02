// Login + register screen (toggles between the two modes).
import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { Icon, type IconName } from "../components/Icon";
import { useAuth } from "../auth/AuthContext";
import { ApiError } from "../api/client";

const FEATURES: { icon: IconName; title: string; body: string }[] = [
  {
    icon: "plug",
    title: "One timeline for everything",
    body: "Canvas, Google Calendar, and course feeds — synced automatically.",
  },
  {
    icon: "clock",
    title: "Never miss a deadline",
    body: "Overdue, due today, and coming up — sorted for you.",
  },
  {
    icon: "sparkles",
    title: "Study smarter",
    body: "Contextual study tips tuned to your workload.",
  },
];

export function Login() {
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    if (mode === "register" && password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    setBusy(true);
    try {
      if (mode === "login") await login(email, password);
      else await register(email, password, fullName);
      navigate("/");
    } catch (err) {
      const msg =
        err instanceof ApiError
          ? err.message
          : "Could not connect. Is the backend running?";
      setError(msg);
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Brand panel (desktop only) */}
      <aside className="hidden lg:flex flex-col justify-between w-[44%] max-w-[560px] p-12 text-white brand-mark">
        <div className="flex items-center gap-2.5 font-extrabold text-2xl tracking-tight">
          <span className="grid place-items-center w-10 h-10 rounded-[12px] bg-white/15 border border-white/25">
            <Icon name="check" size={22} />
          </span>
          Trackable
        </div>

        <div>
          <h1 className="text-[2.1rem] leading-tight m-0">
            Every deadline.
            <br />
            One place.
          </h1>
          <ul className="list-none p-0 mt-8 flex flex-col gap-5">
            {FEATURES.map((f) => (
              <li key={f.title} className="flex gap-3.5 items-start">
                <span className="shrink-0 grid place-items-center w-9 h-9 rounded-[10px] bg-white/15 border border-white/20">
                  <Icon name={f.icon} size={17} />
                </span>
                <div>
                  <strong className="block">{f.title}</strong>
                  <span className="text-white/75 text-sm">{f.body}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>

        <p className="text-white/60 text-sm m-0">Built for college students.</p>
      </aside>

      {/* Form panel */}
      <main className="flex-1 grid place-items-center p-5 bg-[radial-gradient(900px_420px_at_50%_-10%,var(--primary-soft),transparent)]">
        <div className="card p-7 md:p-9 w-full max-w-[420px] shadow-lg">
          <div className="flex items-center justify-center gap-2.5 font-extrabold text-2xl pb-2 tracking-tight lg:hidden">
            <span className="grid place-items-center w-9 h-9 rounded-[10px] brand-mark text-white">
              <Icon name="check" size={20} />
            </span>
            Trackable
          </div>
          <h2 className="text-xl text-center mt-0 mb-1 hidden lg:block">
            {mode === "login" ? "Welcome back" : "Create your account"}
          </h2>
          <p className="text-center text-content-muted mt-0 mb-6 text-[0.95rem]">
            {mode === "login"
              ? "Log in and pick up where you left off."
              : "Take control of your deadlines in minutes."}
          </p>

          {error && (
            <div className="notice notice-danger mb-4" role="alert">
              {error}
            </div>
          )}

          <form onSubmit={submit}>
            {mode === "register" && (
              <div className="field">
                <label className="field-label" htmlFor="name">
                  Full name
                </label>
                <input
                  id="name"
                  className="input"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Alex Student"
                  autoComplete="name"
                />
              </div>
            )}
            <div className="field">
              <label className="field-label" htmlFor="email">
                Email
              </label>
              <input
                id="email"
                type="email"
                required
                className="input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@university.edu"
                autoComplete="email"
              />
            </div>
            <div className="field">
              <label className="field-label" htmlFor="password">
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                className="input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={mode === "register" ? "At least 8 characters" : "••••••••"}
                autoComplete={mode === "login" ? "current-password" : "new-password"}
              />
            </div>

            <button type="submit" className="btn btn-primary w-full mt-1" disabled={busy}>
              {busy ? "Please wait…" : mode === "login" ? "Log in" : "Create account"}
            </button>
          </form>

          <p className="text-center text-sm text-content-muted mt-5 mb-0">
            {mode === "login" ? "New to Trackable? " : "Already have an account? "}
            <button
              className="text-primary-strong font-semibold bg-transparent border-0 cursor-pointer p-0 hover:underline"
              onClick={() => {
                setMode(mode === "login" ? "register" : "login");
                setError(null);
              }}
            >
              {mode === "login" ? "Create one" : "Log in"}
            </button>
          </p>
        </div>
      </main>
    </div>
  );
}
