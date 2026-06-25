// Integrations hub: connect providers, sync, view status, disconnect.
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { integrationsApi } from "../api/endpoints";
import { Icon } from "../components/Icon";
import { Modal } from "../components/Modal";
import { CenterSpinner, ErrorState, PageHeader } from "../components/ui";
import { PROVIDER_META } from "../components/itemMeta";
import { useToast } from "../components/Toast";
import { formatDateTime } from "../utils/date";
import type { Connection, ProviderType } from "../api/types";

const CONNECTABLE: ProviderType[] = ["canvas", "google_calendar", "gradescope", "ics"];

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
  });
  const [connecting, setConnecting] = useState<ProviderType | null>(null);
  const [secrets, setSecrets] = useState<Record<string, string>>({});

  const refresh = () => {
    qc.invalidateQueries({ queryKey: ["connections"] });
    qc.invalidateQueries({ queryKey: ["dashboard"] });
    qc.invalidateQueries({ queryKey: ["items"] });
  };

  const connect = useMutation({
    mutationFn: (body: { provider: ProviderType; secrets?: Record<string, string> }) =>
      integrationsApi.connect(body),
    onSuccess: () => {
      refresh();
      notify("Connected");
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

  const sync = useMutation({
    mutationFn: integrationsApi.sync,
    onSuccess: (res) => {
      refresh();
      notify(`Synced — ${res.total_created} new, ${res.total_updated} updated`);
    },
  });

  if (providers.isLoading || connections.isLoading) return <CenterSpinner />;
  if (providers.isError || connections.isError || !providers.data || !connections.data)
    return <ErrorState />;

  const demo = providers.data.demo_mode;
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
        subtitle="Connect your accounts and pull everything into one place."
        action={
          <button
            className="btn btn-primary"
            onClick={() => sync.mutate()}
            disabled={sync.isPending || connections.data.length === 0}
          >
            <Icon name="sync" size={18} /> {sync.isPending ? "Syncing…" : "Sync now"}
          </button>
        }
      />

      {demo && (
        <div className="bg-primary-soft text-primary-strong rounded-sm px-3 py-2.5 text-sm mb-4">
          <strong>Demo mode is on.</strong> Connecting a provider loads realistic sample
          data — no real credentials needed. Set <code>DEMO_MODE=false</code> on the
          backend to use live accounts.
        </div>
      )}

      <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
        {CONNECTABLE.map((provider) => {
          const meta = PROVIDER_META[provider];
          const conn = connectedMap.get(provider);
          return (
            <div key={provider} className="card p-5">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-3">
                  <span className="w-10 h-10 rounded-[10px] grid place-items-center bg-primary-soft text-primary-strong">
                    <Icon name="plug" size={20} />
                  </span>
                  <div>
                    <strong>{meta.label}</strong>
                    {conn && (
                      <span className="badge badge-success ml-2">Connected</span>
                    )}
                  </div>
                </div>
              </div>
              <p className="text-content-muted text-sm mt-3 mb-4">{meta.description}</p>

              {conn ? (
                <div>
                  <div className="text-[0.8rem] text-content-muted mb-3">
                    {conn.last_synced_at
                      ? `Last synced ${formatDateTime(conn.last_synced_at)} · ${conn.last_sync_status}`
                      : "Not synced yet"}
                  </div>
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => disconnect.mutate(conn.id)}
                  >
                    <Icon name="trash" size={16} /> Disconnect
                  </button>
                </div>
              ) : (
                <button
                  className="btn btn-primary btn-sm"
                  onClick={() => handleConnectClick(provider)}
                  disabled={connect.isPending}
                >
                  <Icon name="plus" size={16} /> Connect
                </button>
              )}
            </div>
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
            {SECRET_FIELDS[connecting].map((f) => (
              <div key={f.key} className="flex flex-col gap-1.5 mb-4">
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
                Connect
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
