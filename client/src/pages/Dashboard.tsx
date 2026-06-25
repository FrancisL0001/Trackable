// Dashboard: at-a-glance stats, reminder buckets, and quick study tips.
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { dashboardApi } from "../api/endpoints";
import { Icon, type IconName } from "../components/Icon";
import { ItemList } from "../components/ItemCard";
import { ItemForm } from "../components/ItemForm";
import {
  CenterSpinner,
  EmptyState,
  ErrorState,
  PageHeader,
  SectionTitle,
} from "../components/ui";
import { useItemMutations } from "../hooks/items";
import { useAuth } from "../auth/AuthContext";
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
    <div className="card p-[18px] flex items-center gap-3.5">
      <span className={`w-[38px] h-[38px] rounded-[10px] grid place-items-center ${toneClass[tone]}`}>
        <Icon name={icon} size={20} />
      </span>
      <div>
        <div className="text-[2rem] font-extrabold leading-none">{value}</div>
        <div className="text-content-muted text-[0.85rem] mt-1.5">{label}</div>
      </div>
    </div>
  );
}

export function Dashboard() {
  const { user } = useAuth();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["dashboard"],
    queryFn: dashboardApi.dashboard,
  });
  const tips = useQuery({ queryKey: ["study-tips"], queryFn: dashboardApi.studyTips });
  const { toggle, create } = useItemMutations();
  const [showForm, setShowForm] = useState(false);

  if (isLoading) return <CenterSpinner label="Loading your dashboard…" />;
  if (isError || !data) return <ErrorState />;

  const { stats, reminders } = data;
  const firstName = (user?.full_name || "there").split(" ")[0];
  const hasAny =
    reminders.overdue.length +
      reminders.today.length +
      reminders.soon.length +
      reminders.upcoming.length >
    0;

  const onToggle = (item: Item) => toggle.mutate(item);

  return (
    <div>
      <PageHeader
        title={`Hi, ${firstName} 👋`}
        subtitle="Here's what's on your plate."
        action={
          <button className="btn btn-primary" onClick={() => setShowForm(true)}>
            <Icon name="plus" size={18} /> New item
          </button>
        }
      />

      <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
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
          <SectionTitle icon="calendar" count={reminders.soon.length}>
            Next 7 days
          </SectionTitle>
          <ItemList items={reminders.soon} onToggle={onToggle} />
        </>
      )}

      {tips.data && tips.data.length > 0 && (
        <>
          <SectionTitle icon="bulb">Study tip</SectionTitle>
          <div className="card p-5 flex flex-col gap-2">
            <span className="w-[38px] h-[38px] rounded-[10px] grid place-items-center bg-accent-soft text-accent">
              <Icon name="bulb" size={20} />
            </span>
            <strong>{tips.data[0].title}</strong>
            <p className="text-content-muted m-0">{tips.data[0].body}</p>
            <Link to="/study-tips" className="text-sm font-semibold mt-1">
              More tips →
            </Link>
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
