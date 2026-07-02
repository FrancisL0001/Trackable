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

/** Shimmering placeholder blocks shown while a page's data loads. */
export function PageSkeleton() {
  return (
    <div aria-hidden="true" className="anim-fade">
      <div className="skeleton h-8 w-52 mb-2" />
      <div className="skeleton h-4 w-72 mb-7" />
      <div className="grid gap-4 grid-cols-2 lg:grid-cols-4 mb-7">
        {Array.from({ length: 4 }, (_, i) => (
          <div key={i} className="skeleton h-[86px]" />
        ))}
      </div>
      <div className="skeleton h-4 w-32 mb-3" />
      <div className="skeleton h-40" />
    </div>
  );
}

export function EmptyState({
  icon = "inbox",
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
      <span className="inline-grid place-items-center w-14 h-14 rounded-full bg-primary-soft text-primary-strong mb-3">
        <Icon name={icon} size={25} />
      </span>
      <p className="font-semibold text-content m-0">{title}</p>
      {hint && <p className="mt-1 text-sm m-0">{hint}</p>}
      {action && <div className="mt-4 flex justify-center">{action}</div>}
    </div>
  );
}

export function PageHeader({
  title,
  subtitle,
  action,
}: {
  title: ReactNode;
  subtitle?: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="flex items-end justify-between gap-4 flex-wrap mb-6">
      <div>
        <h1 className="text-[1.55rem] md:text-[1.8rem] m-0">{title}</h1>
        {subtitle && <p className="mt-1 text-content-muted m-0 text-[0.95rem]">{subtitle}</p>}
      </div>
      {action && <div className="flex items-center gap-2">{action}</div>}
    </div>
  );
}

export function ErrorState({ message }: { message?: string }) {
  return (
    <div className="notice notice-danger" role="alert">
      <Icon name="alert" size={18} className="shrink-0 mt-0.5" />
      <span>{message ?? "Something went wrong. Please try again."}</span>
    </div>
  );
}

export function SectionTitle({
  icon,
  children,
  count,
  action,
}: {
  icon?: IconName;
  children: ReactNode;
  count?: number;
  action?: ReactNode;
}) {
  return (
    <div className="flex items-center justify-between gap-3 mt-7 mb-2.5">
      <h2 className="flex items-center gap-2 text-xs uppercase tracking-[0.08em] text-content-faint font-bold m-0">
        {icon && <Icon name={icon} size={14} />}
        {children}
        {count !== undefined && (
          <span className="grid place-items-center min-w-5 h-5 px-1.5 rounded-full bg-surface-2 text-content-muted text-[0.68rem] tabular-nums normal-case tracking-normal">
            {count}
          </span>
        )}
      </h2>
      {action}
    </div>
  );
}

/** "Showing X of Y" hint rendered when a paginated list is truncated. */
export function TruncationHint({ shown, total }: { shown: number; total: number }) {
  if (shown >= total) return null;
  return (
    <p className="text-[0.8rem] text-content-faint mt-2.5 mb-0 text-center">
      Showing the {shown} most urgent of {total} items.
    </p>
  );
}
