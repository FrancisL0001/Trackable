// Small presentational building blocks shared across pages.
import type { ReactNode } from "react";
import { Icon, type IconName } from "./Icon";

export function Spinner({ label }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 text-content-muted" role="status">
      <span className="spin" aria-hidden="true" />
      {label && <span>{label}</span>}
    </div>
  );
}

export function CenterSpinner({ label }: { label?: string }) {
  return (
    <div className="grid place-items-center min-h-[60vh]">
      <Spinner label={label} />
    </div>
  );
}

export function EmptyState({
  icon = "task",
  title,
  hint,
  action,
}: {
  icon?: IconName;
  title: string;
  hint?: string;
  action?: ReactNode;
}) {
  return (
    <div className="text-center py-12 px-5 text-content-muted">
      <span className="inline-grid place-items-center w-14 h-14 rounded-lg bg-surface-2 text-content-faint mb-3">
        <Icon name={icon} size={26} />
      </span>
      <p className="font-semibold text-content">{title}</p>
      {hint && <p className="mt-1 text-sm">{hint}</p>}
      {action && <div className="mt-4 flex justify-center">{action}</div>}
    </div>
  );
}

export function PageHeader({
  title,
  subtitle,
  action,
}: {
  title: string;
  subtitle?: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex items-end justify-between gap-4 flex-wrap mb-5">
      <div>
        <h1 className="text-2xl md:text-[1.7rem] m-0">{title}</h1>
        {subtitle && <p className="mt-1 text-content-muted m-0">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}

export function ErrorState({ message }: { message?: string }) {
  return (
    <div className="card p-5 text-danger bg-danger-soft border-0">
      {message ?? "Something went wrong. Please try again."}
    </div>
  );
}

export function SectionTitle({
  icon,
  children,
  count,
}: {
  icon?: IconName;
  children: ReactNode;
  count?: number;
}) {
  return (
    <h2 className="flex items-center gap-2 text-xs uppercase tracking-wider text-content-faint font-bold mt-6 mb-2.5">
      {icon && <Icon name={icon} size={14} />}
      {children}
      {count !== undefined && <span className="text-content-faint">({count})</span>}
    </h2>
  );
}
