// Integrations hub: connect providers, watch background sync progress, disconnect.
// Sync is asynchronous server-side: POST /sync queues work, and this page polls
// the connections list while any connection is queued/running.
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { integrationsApi } from "../api/endpoints";
import { Icon } from "../components/Icon";
import { Modal } from "../components/Modal";
import { CenterSpinner, ErrorState, PageHeader } from "../components/ui";
import { PROVIDER_META } from "../components/itemMeta";
import { useToast } from "../components/Toast";
import { formatDateTime } from "../utils/date";
import type { Connection, ProviderInfo, ProviderType, SyncStatus } from "../api/types";

// Secret fields required per provider when NOT in demo mode.
const SECRET_FIELDS: Record<string, { key: string; label: string; type?: string }[]> = {
  canvas: [
    { key: "token", label: "Canvas access token", type: "password" },
    { key: "base_url", label: "Canvas URL (optional)" },
  ],
  google_calendar: [{ key: "ical_url", label: "Secret iCal URL" }],
  gradescope: [
    { key: "email", label: "Email" },
    { key: "password", label: "Password", type: "password" },
  ],
  ics: [{ key: "url", label: "Calendar feed URL (.ics)" }],
};

const PENDING: SyncStatus[] = ["queued", "running"];

function SyncStatusBadge({ conn }: { conn: Connection }) {
  if (!conn.is_active) return <span className="badge">Paused</span>;
  switch (conn.sync_status) {
    case "queued":
    case "running":
      return (
        <span className="badge badge-primary">
          <span className="spin !w-3 !h-3 !border-2" aria-hidden="true" /> Syncing
        </span>
      );
    case "ok":
      return <span className="badge badge-success">Synced</span>;
    case "partial":
      return <span className="badge badge-warning">Partial sync</span>;
    case "error":
      return <span className="badge badge-danger">Sync failed</span>;
    default:
      return <span className="badge">Connected</span>;
  }
}

function ProviderCard({
  info,
  conn,
  demo,
  onConnect,
  onDisconnect,
  onToggle,
  busy,
}: {
  info: ProviderInfo;
  conn: Connection | undefined;
  demo: boolean;
  onConnect: () => void;
  onDisconnect: () => void;
  onToggle: (active: boolean) => void;
  busy: boolean;
}) {
  const meta = PROVIDER_META[info.id];
  return (
    <div className="card card-hover p-5 flex flex-col">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0">
          <span
            className={`shrink-0 w-10 h-10 rounded-[12px] grid place-items-center font-extrabold text-sm ${meta.tone}`}
            aria-hidden="true"
          >
            {meta.monogram}
          </span>
          <div className="min-w-0">
            <strong className="block truncate">{info.label}</strong>
            {!info.live_supported && demo && (
              <span className="badge badge-warning mt-0.5">Demo only</span>
            )}
          </div>
        </div>
        {conn && <SyncStatusBadge conn={conn} />}
      </div>

      <p className="text-content-muted text-sm mt-3 mb-4">{info.description}</p>

      {conn ? (
        <div className="mt-auto">
          <div className="text-[0.78rem] text-content-muted mb-3">
            {conn.last_synced_at
              ? `Last synced ${formatDateTime(conn.last_synced_at)}`
              : "First sync in progress…"}
            {conn.sync_status === "error" && conn.last_sync_error && (
              <span className="block text-danger mt-1">{conn.last_sync_error}</span>
            )}
            {conn.sync_status === "partial" && conn.last_sync_error && (
              <span className="block text-warning mt-1">{conn.last_sync_error}</span>
            )}
          </div>
          <div className="flex gap-2 flex-wrap">
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => onToggle(!conn.is_active)}
              disabled={busy}
            >
              {conn.is_active ? "Pause" : "Resume"}
            </button>
            <button className="btn btn-danger btn-sm" onClick={onDisconnect} disabled={busy}>
              <Icon name="trash" size={15} /> Disconnect
            </button>
          </div>
        </div>
      ) : (
        <div className="mt-auto">
          <button className="btn btn-primary btn-sm" onClick={onConnect} disabled={busy}>
            <Icon name="plus" size={15} /> Connect
          </button>
          {info.note && (
            <p className="text-[0.75rem] text-content-faint mt-2.5 mb-0">{info.note}</p>
          )}
        </div>
      )}
    </div>
  );
}

export function Integrations() {
  const qc = useQueryClient();
  const { notify } = useToast();
  const providers = useQuery({
    queryKey: ["providers"],
    queryFn: integrationsApi.providers,
  });
  const connections = useQuery({
    queryKey: ["connections"],
    queryFn: integrationsApi.connections,
    // Poll while any sync is queued/running so status chips update live.
    refetchInterval: (query) =>
      query.state.data?.some((c) => PENDING.includes(c.sync_status)) ? 1500 : false,
  });
  const [connecting, setConnecting] = useState<ProviderType | null>(null);
  const [secrets, setSecrets] = useState<Record<string, string>>({});
  const watchingSync = useRef(false);

  const anyPending = connections.data?.some((c) => PENDING.includes(c.sync_status)) ?? false;

  const refresh = () => {
    qc.invalidateQueries({ queryKey: ["connections"] });
    qc.invalidateQueries({ queryKey: ["dashboard"] });
    qc.invalidateQueries({ queryKey: ["reminders"] });
    qc.invalidateQueries({ queryKey: ["items"] });
  };

  // When a watched sync settles, refresh data and let the user know.
  useEffect(() => {
    if (watchingSync.current && !anyPending && connections.data?.length) {
      watchingSync.current = false;
      refresh();
      const failed = connections.data.filter((c) => c.sync_status === "error").length;
      notify(failed ? `Sync finished — ${failed} connection(s) failed` : "Sync complete");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [anyPending, connections.data]);

  const connect = useMutation({
    mutationFn: (body: { provider: ProviderType; secrets?: Record<string, string> }) =>
      integrationsApi.connect(body),
    onSuccess: () => {
      watchingSync.current = true;
      refresh();
      notify("Connected — first sync started");
      setConnecting(null);
      setSecrets({});
    },
  });

  const disconnect = useMutation({
    mutationFn: (id: number) => integrationsApi.disconnect(id),
    onSuccess: () => {
      refresh();
      notify("Disconnected");
    },
  });

  const toggleActive = useMutation({
    mutationFn: ({ id, active }: { id: number; active: boolean }) =>
      integrationsApi.toggle(id, active),
    onSuccess: () => refresh(),
  });

  const sync = useMutation({
    mutationFn: integrationsApi.sync,
    onSuccess: (res) => {
      if (res.queued.length) {
        watchingSync.current = true;
        notify(`Syncing ${res.queued.length} connection(s)…`);
      } else {
        notify("Nothing to sync");
      }
      qc.invalidateQueries({ queryKey: ["connections"] });
    },
  });

  if (providers.isLoading || connections.isLoading) return <CenterSpinner />;
  if (providers.isError || connections.isError || !providers.data || !connections.data)
    return <ErrorState />;

  const { demo_mode: demo, sync_interval_minutes: interval } = providers.data;
  const connectedMap = new Map<ProviderType, Connection>(
    connections.data.map((c) => [c.provider, c])
  );

  const handleConnectClick = (provider: ProviderType) => {
    if (demo) connect.mutate({ provider });
    else setConnecting(provider);
  };

  return (
    <div>
      <PageHeader
        title="Integrations"
        subtitle={`Everything in one place — connected accounts refresh automatically every ${interval} minutes.`}
        action={
          <button
            className="btn btn-primary"
            onClick={() => sync.mutate()}
            disabled={sync.isPending || anyPending || connections.data.length === 0}
          >
            <Icon name="sync" size={18} />
            {anyPending || sync.isPending ? "Syncing…" : "Sync now"}
          </button>
        }
      />

      {demo && (
        <div className="notice notice-info mb-5">
          <Icon name="sparkles" size={17} className="shrink-0 mt-0.5 text-primary-strong" />
          <span>
            <strong>Demo mode is on.</strong> Connecting a provider loads realistic
            sample data — no real credentials needed. Set <code>DEMO_MODE=false</code>{" "}
            on the backend to use live accounts.
          </span>
        </div>
      )}

      <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
        {providers.data.providers.map((info) => {
          const conn = connectedMap.get(info.id);
          return (
            <ProviderCard
              key={info.id}
              info={info}
              conn={conn}
              demo={demo}
              busy={connect.isPending || disconnect.isPending || toggleActive.isPending}
              onConnect={() => handleConnectClick(info.id)}
              onDisconnect={() => conn && disconnect.mutate(conn.id)}
              onToggle={(active) => conn && toggleActive.mutate({ id: conn.id, active })}
            />
          );
        })}
      </div>

      {connecting && (
        <Modal
          title={`Connect ${PROVIDER_META[connecting].label}`}
          onClose={() => {
            setConnecting(null);
            setSecrets({});
          }}
        >
          <form
            onSubmit={(e) => {
              e.preventDefault();
              connect.mutate({ provider: connecting, secrets });
            }}
          >
            {connect.isError && (
              <div className="notice notice-danger mb-4">
                {connect.error instanceof Error
                  ? connect.error.message
                  : "Could not connect."}
              </div>
            )}
            {SECRET_FIELDS[connecting].map((f) => (
              <div key={f.key} className="field">
                <label className="field-label" htmlFor={`sec-${f.key}`}>
                  {f.label}
                </label>
                <input
                  id={`sec-${f.key}`}
                  type={f.type ?? "text"}
                  className="input"
                  value={secrets[f.key] ?? ""}
                  onChange={(e) =>
                    setSecrets((s) => ({ ...s, [f.key]: e.target.value }))
                  }
                />
              </div>
            ))}
            <div className="flex justify-end gap-2.5">
              <button
                type="button"
                className="btn btn-ghost"
                onClick={() => {
                  setConnecting(null);
                  setSecrets({});
                }}
              >
                Cancel
              </button>
              <button type="submit" className="btn btn-primary" disabled={connect.isPending}>
                {connect.isPending ? "Connecting…" : "Connect"}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
