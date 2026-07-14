// Study tips page: contextual tips surfaced from the backend.
import { useQuery } from "@tanstack/react-query";
import { dashboardApi } from "../api/endpoints";
import { Icon } from "../components/Icon";
import { ErrorState, PageHeader, PageSkeleton } from "../components/ui";

export function StudyTips() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["study-tips"],
    queryFn: dashboardApi.studyTips,
  });

  if (isLoading) return <PageSkeleton />;
  if (isError || !data) return <ErrorState />;

  return (
    <div>
      <PageHeader
        title="Study tips"
        subtitle="Small habits that make a big difference. Tailored to your workload."
      />
      <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
        {data.map((tip, i) => (
          <div key={i} className="card card-hover p-5 flex flex-col gap-2.5">
            <div className="flex items-center justify-between gap-3">
              <span className="w-10 h-10 rounded-[12px] grid place-items-center bg-accent-soft text-accent">
                <Icon name="sparkles" size={19} />
              </span>
              <span className="badge">{tip.category}</span>
            </div>
            <strong className="text-[1.05rem] leading-snug">{tip.title}</strong>
            <p className="text-content-muted m-0 text-[0.95rem]">{tip.body}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
