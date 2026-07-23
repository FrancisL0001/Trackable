// Full-page error states: server unreachable, server error, not found, crash.
// `QueryError` picks the right variant from a thrown ApiError automatically.
import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { ApiError } from "../api/client";
import { Icon, type IconName } from "./Icon";

export type ErrorKind = "offline" | "server" | "notfound" | "generic";

const COPY: Record<
  ErrorKind,
  { icon: IconName; tone: string; title: string; hint: string }
> = {
  offline: {
    icon: "offline",
    tone: "bg-warning-soft text-warning",
    title: "Can't reach the server",
    hint: "Trackable couldn't connect. Check your internet connection — or, if you're running locally, make sure the backend is up.",
  },
  server: {
    icon: "alert",
    tone: "bg-danger-soft text-danger",
    title: "Something broke on our end",
    hint: "The server hit an unexpected error. Your data is safe — give it a moment and try again.",
  },
  notfound: {
    icon: "search",
    tone: "bg-primary-soft text-primary-strong",
    title: "Page not found",
    hint: "This page doesn't exist or may have moved.",
  },
  generic: {
    icon: "alert",
    tone: "bg-danger-soft text-danger",
    title: "Something went wrong",
    hint: "An unexpected error occurred. Try again, and if it keeps happening, reload the page.",
  },
};

/** Classify a thrown error into a page variant. */
export function errorKind(error: unknown): ErrorKind {
  if (error instanceof ApiError) {
    if (error.status === 0) return "offline";
    if (error.status === 404) return "notfound";
    if (error.status >= 500) return "server";
  }
  return "generic";
}

export function ErrorPage({
  kind,
  onRetry,
  fullScreen = false,
  detail,
  action,
}: {
  kind: ErrorKind;
  onRetry?: () => void;
  /** Center on the whole viewport (boot/crash) vs. within the page area. */
  fullScreen?: boolean;
  /** Optional technical detail shown small under the hint. */
  detail?: string;
  /** Extra action rendered next to Retry (e.g. a link home). */
  action?: ReactNode;
}) {
  const copy = COPY[kind];
  return (
    <div
      className={`grid place-items-center p-6 text-center ${
        fullScreen ? "min-h-screen" : "min-h-[55vh]"
      }`}
      role="alert"
    >
      <div className="max-w-sm">
        <span
          className={`inline-grid place-items-center w-16 h-16 rounded-full mb-4 ${copy.tone}`}
        >
          <Icon name={copy.icon} size={28} />
        </span>
        <h1 className="text-xl m-0">{copy.title}</h1>
        <p className="text-content-muted mt-2 mb-0 text-[0.95rem]">{copy.hint}</p>
        {detail && (
          <p className="text-content-faint text-[0.78rem] mt-2 mb-0 break-words">
            {detail}
          </p>
        )}
        <div className="mt-6 flex justify-center gap-2.5 flex-wrap">
          {onRetry && (
            <button className="btn btn-primary" onClick={onRetry}>
              <Icon name="sync" size={17} /> Try again
            </button>
          )}
          {action}
        </div>
      </div>
    </div>
  );
}

/** Drop-in for pages: renders the right full-page state for a failed query. */
export function QueryError({
  error,
  onRetry,
}: {
  error: unknown;
  onRetry?: () => void;
}) {
  const kind = errorKind(error);
  const detail =
    kind === "generic" && error instanceof Error ? error.message : undefined;
  return (
    <ErrorPage
      kind={kind}
      onRetry={onRetry}
      detail={detail}
      action={
        kind === "notfound" ? (
          <Link to="/" className="btn btn-ghost">
            Back to dashboard
          </Link>
        ) : undefined
      }
    />
  );
}
