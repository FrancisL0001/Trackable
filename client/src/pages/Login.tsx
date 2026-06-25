// Login + register screen (toggles between the two modes).
import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { Icon } from "../components/Icon";
import { useAuth } from "../auth/AuthContext";
import { ApiError } from "../api/client";

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
    <div className="min-h-screen grid place-items-center p-5 bg-[radial-gradient(1200px_500px_at_50%_-10%,var(--primary-soft),transparent)]">
      <div className="card p-8 w-full max-w-[420px]">
        <div className="flex items-center justify-center gap-2.5 font-extrabold text-2xl pb-2 tracking-tight">
          <span className="grid place-items-center w-9 h-9 rounded-[10px] bg-primary text-white">
            <Icon name="check" size={22} />
          </span>
          Trackable
        </div>
        <p className="text-center text-content-muted mt-0 mb-6">
          {mode === "login"
            ? "Welcome back. Let's get organized."
            : "Create your account and take control of your deadlines."}
        </p>

        {error && (
          <div className="bg-danger-soft text-danger rounded-sm px-3 py-2.5 text-sm mb-3.5">
            {error}
          </div>
        )}

        <form onSubmit={submit}>
          {mode === "register" && (
            <div className="flex flex-col gap-1.5 mb-4">
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
          <div className="flex flex-col gap-1.5 mb-4">
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
          <div className="flex flex-col gap-1.5 mb-4">
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

          <button type="submit" className="btn btn-primary w-full" disabled={busy}>
            {busy ? "Please wait…" : mode === "login" ? "Log in" : "Create account"}
          </button>
        </form>

        <p className="text-center text-sm text-content-muted mt-5 mb-0">
          {mode === "login" ? "New to Trackable? " : "Already have an account? "}
          <button
            className="text-primary font-semibold bg-transparent border-0 cursor-pointer p-0"
            onClick={() => {
              setMode(mode === "login" ? "register" : "login");
              setError(null);
            }}
          >
            {mode === "login" ? "Create one" : "Log in"}
          </button>
        </p>
      </div>
    </div>
  );
}
