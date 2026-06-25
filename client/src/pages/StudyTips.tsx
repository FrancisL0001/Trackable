// Study tips page: contextual tips surfaced from the backend.
import { useQuery } from "@tanstack/react-query";
import { dashboardApi } from "../api/endpoints";
import { Icon } from "../components/Icon";
import { CenterSpinner, ErrorState, PageHeader } from "../components/ui";

export function StudyTips() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["study-tips"],
    queryFn: dashboardApi.studyTips,
  });

  if (isLoading) return <CenterSpinner label="Gathering tips…" />;
  if (isError || !data) return <ErrorState />;

  return (
    <div>
      <PageHeader
        title="Study tips"
        subtitle="Small habits that make a big difference. Tailored to your workload."
      />
      <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
        {data.map((tip, i) => (
          <div key={i} className="card p-5 flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <span className="w-[38px] h-[38px] rounded-[10px] grid place-items-center bg-accent-soft text-accent">
                <Icon name="bulb" size={20} />
              </span>
              <span className="badge">{tip.category}</span>
            </div>
            <strong className="text-[1.05rem]">{tip.title}</strong>
            <p className="text-content-muted m-0">{tip.body}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
