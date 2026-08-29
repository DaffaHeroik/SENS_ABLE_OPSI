import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { trpc } from "@/lib/trpc";
import { Activity, CircleAlert, Copy, Cpu, Database, KeyRound, RadioTower, RefreshCw, ShieldCheck } from "lucide-react";
import { FormEvent, useState } from "react";
import { Link } from "wouter";

function formatTime(value: Date | string | null | undefined) {
  if (!value) return "No accepted signal yet";
  return new Intl.DateTimeFormat("en-GB", { dateStyle: "medium", timeStyle: "medium" }).format(new Date(value));
}

function MetricCard({ icon: Icon, label, value, detail }: { icon: typeof Activity; label: string; value: string | number; detail: string }) {
  return (
    <article className="cad-frame relative overflow-hidden p-5">
      <Icon className="absolute right-4 top-4 h-5 w-5 text-cyan-200/70" />
      <p className="blueprint-label">{label}</p>
      <p className="mt-3 text-3xl font-bold tracking-tight text-white">{value}</p>
      <p className="mt-2 text-sm text-slate-300">{detail}</p>
    </article>
  );
}

export default function Home() {
  const [deviceId, setDeviceId] = useState("SENSABLE-01");
  const [newSecret, setNewSecret] = useState<{ deviceId: string; deviceSecret: string } | null>(null);
  const overview = trpc.gateway.overview.useQuery(undefined, { refetchInterval: 15_000 });
  const registerDevice = trpc.gateway.registerDevice.useMutation({
    onSuccess: result => {
      setNewSecret(result);
      overview.refetch();
    },
  });

  const submit = (event: FormEvent) => {
    event.preventDefault();
    setNewSecret(null);
    registerDevice.mutate({ deviceId: deviceId.trim().toUpperCase() });
  };

  const isLocalPreview = ["127.0.0.1", "localhost"].includes(window.location.hostname);
  const publicOrigin = isLocalPreview ? "https://<published-gateway-domain>" : window.location.origin;

  return (
    <div className="mx-auto max-w-7xl space-y-7">
      <section className="cad-frame relative overflow-hidden p-6 lg:p-8">
        <div className="absolute -right-10 -top-14 h-52 w-52 rounded-full border border-cyan-100/20" />
        <div className="absolute right-8 top-8 text-[10px] font-bold tracking-[0.2em] text-cyan-200/55">NODE // HTTPS // TEST-ONLY</div>
        <p className="blueprint-label">Gateway control plane</p>
        <div className="mt-3 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">ESP32 test ingestion</h1>
            <p className="mt-3 max-w-2xl leading-7 text-slate-300">Authenticated HTTPS intake for non-identifying sensor test signals. Names, SubjectID values, and glucometer-reference records are rejected before storage.</p>
          </div>
          <Button variant="outline" onClick={() => overview.refetch()} className="border-cyan-100/35 bg-cyan-100/5 text-cyan-100 hover:bg-cyan-200/10 hover:text-white">
            <RefreshCw className="mr-2 h-4 w-4" /> Refresh status
          </Button>
        </div>
      </section>

      {overview.error ? (
        <section className="flex items-start gap-3 border border-amber-300/40 bg-amber-200/10 p-4 text-amber-100">
          <CircleAlert className="mt-0.5 h-5 w-5 shrink-0" />
          <div><p className="font-semibold">Owner access required</p><p className="mt-1 text-sm text-amber-100/80">{overview.error.message}</p></div>
        </section>
      ) : null}

      <section className="grid gap-4 md:grid-cols-3">
        <MetricCard icon={RadioTower} label="Active devices" value={overview.data?.stats.activeDevices ?? "—"} detail="Registered device tokens that are not revoked" />
        <MetricCard icon={Database} label="Accepted readings" value={overview.data?.stats.totalAcceptedReadings ?? "—"} detail="Test signals accepted after validation" />
        <MetricCard icon={ShieldCheck} label="Ingestion status" value="HTTPS" detail="Public endpoint protected by a per-device token" />
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.95fr_1.45fr]">
        <article className="cad-frame p-6">
          <div className="flex items-center gap-3"><div className="grid h-10 w-10 place-items-center border border-cyan-300/40 bg-cyan-300/10"><KeyRound className="h-5 w-5 text-cyan-100" /></div><div><p className="blueprint-label">Device onboarding</p><h2 className="font-semibold text-white">Create device token</h2></div></div>
          <p className="mt-4 text-sm leading-6 text-slate-300">The token is displayed exactly once. Store it in the ESP32 firmware as a secret and never include it in a report or public repository.</p>
          <form onSubmit={submit} className="mt-5 space-y-3">
            <label className="text-sm font-medium text-slate-200" htmlFor="device-id">Device ID</label>
            <Input id="device-id" value={deviceId} onChange={event => setDeviceId(event.target.value)} placeholder="SENSABLE-01" className="border-cyan-100/25 bg-[#031337] text-white placeholder:text-slate-500" />
            <Button type="submit" disabled={registerDevice.isPending} className="w-full bg-cyan-300 text-blue-950 hover:bg-cyan-200">{registerDevice.isPending ? "Creating token…" : "Create protected device token"}</Button>
            {registerDevice.error ? <p className="text-sm text-red-200">{registerDevice.error.message}</p> : null}
          </form>
          {newSecret ? (
            <div className="mt-5 border border-emerald-300/40 bg-emerald-300/10 p-4">
              <p className="text-sm font-semibold text-emerald-100">Token created for {newSecret.deviceId}</p>
              <p className="mt-2 break-all font-mono text-xs leading-6 text-white">{newSecret.deviceSecret}</p>
              <Button variant="outline" onClick={() => navigator.clipboard.writeText(newSecret.deviceSecret)} className="mt-3 border-emerald-200/40 text-emerald-100 hover:bg-emerald-200/10"><Copy className="mr-2 h-4 w-4" /> Copy once</Button>
            </div>
          ) : null}
        </article>

        <article className="cad-frame overflow-hidden">
          <div className="flex items-center justify-between border-b border-cyan-100/15 px-6 py-5"><div><p className="blueprint-label">Live ledger</p><h2 className="mt-1 text-lg font-semibold text-white">Recent accepted test readings</h2></div><span className="text-xs text-slate-400">Server timestamp</span></div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[680px] text-left text-sm">
              <thead className="border-b border-cyan-100/10 text-xs uppercase tracking-[0.14em] text-cyan-100/70"><tr><th className="px-6 py-4">Received</th><th className="px-4 py-4">Device</th><th className="px-4 py-4">IR</th><th className="px-4 py-4">RED</th><th className="px-4 py-4">HR</th><th className="px-4 py-4">Temp</th></tr></thead>
              <tbody className="divide-y divide-cyan-100/10 text-slate-200">
                {overview.data?.readings.length ? overview.data.readings.map(reading => <tr key={reading.id} className="hover:bg-cyan-200/5"><td className="px-6 py-4 text-slate-300">{formatTime(reading.receivedAt)}</td><td className="px-4 py-4 font-mono text-cyan-100">{reading.deviceId}</td><td className="px-4 py-4">{reading.irMean.toFixed(0)}</td><td className="px-4 py-4">{reading.redMean.toFixed(0)}</td><td className="px-4 py-4">{reading.heartRateBpm?.toFixed(1) ?? "—"}</td><td className="px-4 py-4">{reading.temperatureC?.toFixed(1) ?? "—"}</td></tr>) : <tr><td colSpan={6} className="px-6 py-12 text-center text-slate-400">No accepted test readings yet. Register a device, then send the sample payload from the Connection page.</td></tr>}
              </tbody>
            </table>
          </div>
        </article>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <article className="cad-frame p-5"><p className="blueprint-label">Public health endpoint</p><p className="mt-2 break-all font-mono text-sm text-cyan-100">{publicOrigin}/api/health</p><p className="mt-3 text-sm leading-6 text-slate-300">After publishing, this becomes the HTTPS gateway address. It returns only availability and server time, never readings, device secrets, or identity data.</p></article>
        <article className="cad-frame p-5"><p className="blueprint-label">Next system step</p><p className="mt-2 font-semibold text-white">Connect an ESP32 securely</p><p className="mt-3 text-sm leading-6 text-slate-300">Use the HTTPS endpoint and one-time device token. The connection guide contains the exact JSON contract and Arduino request pattern.</p><Link href="/connection" className="mt-4 inline-flex items-center text-sm font-semibold text-cyan-100 hover:text-cyan-200">Open connection guide →</Link></article>
      </section>
    </div>
  );
}
