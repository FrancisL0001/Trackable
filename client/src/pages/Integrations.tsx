// Integrations hub: connect providers, watch background sync progress, disconnect.
// Sync is asynchronous server-side: POST /sync queues work, and this page polls
// the connections list while any connection is queued/running.
//
// Multi-capable providers (per-course ICS feeds, Google calendars) can hold
// several named connections at once — one per course website.
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { integrationsApi } from "../api/endpoints";
import { Icon } from "../components/Icon";
import { Modal } from "../components/Modal";
import { QueryError } from "../components/ErrorPage";
import { CenterSpinner, PageHeader } from "../components/ui";
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
  web_page: [{ key: "url", label: "Course page URL (the assignments page)" }],
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

/** One connected feed/account row inside a provider card. */
function ConnectionRow({
  conn,
  showName,
  onDisconnect,
  onToggle,
  busy,
}: {
  conn: Connection;
  showName: boolean;
  onDisconnect: () => void;
  onToggle: (active: boolean) => void;
  busy: boolean;
}) {
  return (
    <div className="flex items-center gap-3 py-2.5 min-w-0">
      <div className="flex-1 min-w-0">
        {showName && (
          <div className="font-semibold text-[0.9rem] truncate">{conn.display_name}</div>
        )}
        <div className="text-[0.78rem] text-content-muted truncate">
          {conn.last_synced_at
            ? `Last synced ${formatDateTime(conn.last_synced_at)}`
            : "First sync in progress…"}
        </div>
        {(conn.sync_status === "error" || conn.sync_status === "partial") &&
          conn.last_sync_error && (
            <div
              className={`text-[0.78rem] mt-0.5 ${
                conn.sync_status === "error" ? "text-danger" : "text-warning"
              }`}
            >
              {conn.last_sync_error}
            </div>
          )}
      </div>
      <SyncStatusBadge conn={conn} />
      <div className="flex gap-1 shrink-0">
        <button
          className="icon-btn !w-9 !h-9"
          onClick={() => onToggle(!conn.is_active)}
          disabled={busy}
          aria-label={conn.is_active ? `Pause ${conn.display_name}` : `Resume ${conn.display_name}`}
          title={conn.is_active ? "Pause syncing" : "Resume syncing"}
        >
          <Icon name={conn.is_active ? "close" : "sync"} size={15} />
        </button>
        <button
          className="icon-btn !w-9 !h-9 hover:!text-danger hover:!border-danger"
          onClick={onDisconnect}
          disabled={busy}
          aria-label={`Disconnect ${conn.display_name}`}
          title="Disconnect (removes its synced items)"
        >
          <Icon name="trash" size={15} />
        </button>
      </div>
    </div>
  );
}

function ProviderCard({
  info,
  conns,
  onConnect,
  onDisconnect,
  onToggle,
  busy,
}: {
  info: ProviderInfo;
  conns: Connection[];
  onConnect: () => void;
  onDisconnect: (conn: Connection) => void;
  onToggle: (conn: Connection, active: boolean) => void;
  busy: boolean;
}) {
  const meta = PROVIDER_META[info.id];
  const connected = conns.length > 0;
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
            <div className="flex gap-1.5 mt-0.5">
              {info.multi && connected && (
                <span className="badge badge-primary">
                  {conns.length} {conns.length === 1 ? "feed" : "feeds"}
                </span>
              )}
            </div>
          </div>
        </div>
        {!info.multi && conns[0] && <SyncStatusBadge conn={conns[0]} />}
      </div>

      <p className="text-content-muted text-sm mt-3 mb-3">{info.description}</p>

      {connected && (
        <div className="divide-y divide-border border-t border-border">
          {conns.map((conn) => (
            <ConnectionRow
              key={conn.id}
              conn={conn}
              showName={info.multi}
              busy={busy}
              onDisconnect={() => onDisconnect(conn)}
              onToggle={(active) => onToggle(conn, active)}
            />
          ))}
        </div>
      )}

      <div className="mt-auto pt-3">
        {(!connected || info.multi) && (
          <button className="btn btn-primary btn-sm" onClick={onConnect} disabled={busy}>
            <Icon name="plus" size={15} />
            {info.multi && connected ? "Add another feed" : "Connect"}
          </button>
        )}
        {!connected && info.note && (
          <p className="text-[0.75rem] text-content-faint mt-2.5 mb-0">{info.note}</p>
        )}
      </div>
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
  const [connecting, setConnecting] = useState<ProviderInfo | null>(null);
  const [displayName, setDisplayName] = useState("");
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

  const closeModal = () => {
    setConnecting(null);
    setDisplayName("");
    setSecrets({});
    connect.reset();
  };

  const connect = useMutation({
    mutationFn: (body: {
      provider: ProviderType;
      display_name?: string;
      secrets?: Record<string, string>;
    }) => integrationsApi.connect(body),
    onSuccess: () => {
      watchingSync.current = true;
      refresh();
      notify("Connected — first sync started");
      closeModal();
    },
  });

  const disconnect = useMutation({
    mutationFn: (id: number) => integrationsApi.disconnect(id),
    onSuccess: () => {
      refresh();
      notify("Disconnected — its items were removed");
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
    return (
      <QueryError
        error={providers.error ?? connections.error}
        onRetry={() => {
          providers.refetch();
          connections.refetch();
        }}
      />
    );

  const { demo_mode: demo, sync_interval_minutes: interval } = providers.data;
  const byProvider = new Map<ProviderType, Connection[]>();
  for (const c of connections.data) {
    const list = byProvider.get(c.provider);
    if (list) list.push(c);
    else byProvider.set(c.provider, [c]);
  }

  const handleConnectClick = (info: ProviderInfo) => {
    // Multi providers always go through the modal (to name the feed); in demo
    // mode single providers connect instantly with sample data.
    if (demo && !info.multi) connect.mutate({ provider: info.id });
    else setConnecting(info);
  };

  const handleDisconnect = (conn: Connection) => {
    const ok = window.confirm(
      `Disconnect “${conn.display_name}”? Items it synced will be removed from your timeline (manual items are kept).`
    );
    if (ok) disconnect.mutate(conn.id);
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
        {providers.data.providers.map((info) => (
          <ProviderCard
            key={info.id}
            info={info}
            conns={byProvider.get(info.id) ?? []}
            busy={connect.isPending || disconnect.isPending || toggleActive.isPending}
            onConnect={() => handleConnectClick(info)}
            onDisconnect={handleDisconnect}
            onToggle={(conn, active) => toggleActive.mutate({ id: conn.id, active })}
          />
        ))}
      </div>

      {connecting && (
        <Modal title={`Connect ${connecting.label}`} onClose={closeModal}>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              connect.mutate({
                provider: connecting.id,
                display_name: displayName.trim() || undefined,
                secrets: demo ? undefined : secrets,
              });
            }}
          >
            {connect.isError && (
              <div className="notice notice-danger mb-4">
                {connect.error instanceof Error
                  ? connect.error.message
                  : "Could not connect."}
              </div>
            )}
            {connecting.multi && (
              <div className="field">
                <label className="field-label" htmlFor="conn-name">
                  Name this feed
                </label>
                <input
                  id="conn-name"
                  className="input"
                  value={displayName}
                  autoFocus
                  onChange={(e) => setDisplayName(e.target.value)}
                  placeholder="e.g. CS 0410"
                />
              </div>
            )}
            {!demo &&
              SECRET_FIELDS[connecting.id].map((f) => (
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
            {demo && connecting.multi && (
              <p className="text-sm text-content-muted mt-0 mb-4">
                Demo mode: this connection will load sample course data. In live
                mode you'd paste the {SECRET_FIELDS[connecting.id][0].label.toLowerCase()}{" "}
                here.
              </p>
            )}
            <div className="flex justify-end gap-2.5">
              <button type="button" className="btn btn-ghost" onClick={closeModal}>
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
