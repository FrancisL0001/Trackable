// Dashboard: at-a-glance stats, reminder buckets, and quick study tips.
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { dashboardApi } from "../api/endpoints";
import { Icon, type IconName } from "../components/Icon";
import { ItemList } from "../components/ItemCard";
import { ItemForm } from "../components/ItemForm";
import { QueryError } from "../components/ErrorPage";
import {
  EmptyState,
  PageHeader,
  PageSkeleton,
  SectionTitle,
} from "../components/ui";
import { useItemMutations } from "../hooks/items";
import { useAuth } from "../auth/AuthContext";
import { useToast } from "../components/Toast";
import type { Item } from "../api/types";

function StatCard({
  icon,
  value,
  label,
  tone = "primary",
}: {
  icon: IconName;
  value: number;
  label: string;
  tone?: "primary" | "danger" | "accent" | "success";
}) {
  const toneClass: Record<string, string> = {
    primary: "bg-primary-soft text-primary-strong",
    danger: "bg-danger-soft text-danger",
    accent: "bg-accent-soft text-accent",
    success: "bg-success-soft text-success",
  };
  return (
    <div className="card card-hover p-4 md:p-[18px] flex items-center gap-3.5 min-w-0">
      <span
        className={`shrink-0 w-10 h-10 rounded-[12px] grid place-items-center ${toneClass[tone]}`}
      >
        <Icon name={icon} size={19} />
      </span>
      <div className="min-w-0">
        <div className="text-[1.7rem] md:text-[1.9rem] font-extrabold leading-none tabular-nums">
          {value}
        </div>
        <div className="text-content-muted text-[0.8rem] mt-1 truncate">{label}</div>
      </div>
    </div>
  );
}

/** Reminder-window preference: how far ahead "coming up" looks. */
function SoonWindowSelect() {
  const { user, updateProfile } = useAuth();
  const { notify } = useToast();
  const [saving, setSaving] = useState(false);
  const days = user?.reminder_soon_days ?? 7;

  const onChange = async (value: number) => {
    setSaving(true);
    try {
      await updateProfile({ reminder_soon_days: value });
      notify(`Reminder window set to ${value} days`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <label className="flex items-center gap-1.5 text-[0.78rem] font-semibold text-content-faint">
      Window
      <select
        className="select !w-auto !py-1 !px-2 !text-[0.8rem] cursor-pointer"
        value={days}
        disabled={saving}
        onChange={(e) => onChange(Number(e.target.value))}
        aria-label="How many days ahead to remind"
      >
        {[3, 5, 7, 14].map((d) => (
          <option key={d} value={d}>
            {d} days
          </option>
        ))}
      </select>
    </label>
  );
}

export function Dashboard() {
  const { user } = useAuth();
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["dashboard"],
    queryFn: dashboardApi.dashboard,
  });
  const tips = useQuery({ queryKey: ["study-tips"], queryFn: dashboardApi.studyTips });
  const { toggle, create } = useItemMutations();
  const [showForm, setShowForm] = useState(false);

  if (isLoading) return <PageSkeleton />;
  if (isError || !data) return <QueryError error={error} onRetry={() => refetch()} />;

  const { stats, reminders } = data;
  const firstName = (user?.full_name || "there").split(" ")[0];
  const today = new Date().toLocaleDateString(undefined, {
    weekday: "long",
    month: "long",
    day: "numeric",
  });
  const hasAny =
    reminders.overdue.length +
      reminders.today.length +
      reminders.soon.length +
      reminders.upcoming.length >
    0;
  const soonDays = user?.reminder_soon_days ?? 7;

  const onToggle = (item: Item) => toggle.mutate(item);

  return (
    <div>
      <PageHeader
        title={`Hi, ${firstName}`}
        subtitle={today}
        action={
          <button className="btn btn-primary" onClick={() => setShowForm(true)}>
            <Icon name="plus" size={18} /> New item
          </button>
        }
      />

      <div className="grid gap-3 md:gap-4 grid-cols-2 lg:grid-cols-4">
        <StatCard icon="alert" value={stats.overdue} label="Overdue" tone="danger" />
        <StatCard icon="clock" value={stats.due_today} label="Due today" tone="accent" />
        <StatCard icon="calendar" value={stats.due_this_week} label="Due this week" />
        <StatCard
          icon="check"
          value={stats.completed_this_week}
          label="Done this week"
          tone="success"
        />
      </div>

      {!hasAny && (
        <div className="card mt-6">
          <EmptyState
            icon="check"
            title="You're all caught up!"
            hint="Connect an account or add an item to start tracking."
            action={
              <Link to="/integrations" className="btn btn-primary">
                <Icon name="plug" size={18} /> Connect accounts
              </Link>
            }
          />
        </div>
      )}

      {reminders.overdue.length > 0 && (
        <>
          <SectionTitle icon="alert" count={reminders.overdue.length}>
            Overdue
          </SectionTitle>
          <ItemList items={reminders.overdue} onToggle={onToggle} />
        </>
      )}
      {reminders.today.length > 0 && (
        <>
          <SectionTitle icon="clock" count={reminders.today.length}>
            Due today
          </SectionTitle>
          <ItemList items={reminders.today} onToggle={onToggle} />
        </>
      )}
      {reminders.soon.length > 0 && (
        <>
          <SectionTitle
            icon="calendar"
            count={reminders.soon.length}
            action={<SoonWindowSelect />}
          >
            Next {soonDays} days
          </SectionTitle>
          <ItemList items={reminders.soon} onToggle={onToggle} />
        </>
      )}

      {tips.data && tips.data.length > 0 && (
        <>
          <SectionTitle icon="bulb">Study tip</SectionTitle>
          <div className="card p-5 flex gap-4 items-start">
            <span className="shrink-0 w-10 h-10 rounded-[12px] grid place-items-center bg-accent-soft text-accent">
              <Icon name="sparkles" size={19} />
            </span>
            <div className="min-w-0">
              <strong>{tips.data[0].title}</strong>
              <p className="text-content-muted m-0 mt-1">{tips.data[0].body}</p>
              <Link
                to="/study-tips"
                className="inline-flex items-center gap-1 text-sm font-semibold mt-2.5 text-primary-strong"
              >
                More tips <Icon name="chevron-right" size={14} />
              </Link>
            </div>
          </div>
        </>
      )}

      {showForm && (
        <ItemForm
          onSubmit={(input) => create.mutateAsync(input).then(() => undefined)}
          onClose={() => setShowForm(false)}
        />
      )}
    </div>
  );
}
