import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { CheckCircle2, CircleAlert, Cpu, Download, Loader2, LockKeyhole, PlugZap, ShieldCheck, Wifi } from "lucide-react";
import { useEffect, useState } from "react";
import { ESPLoader, Transport } from "esptool-js";

type PublicRelease = { id: number; version: string; board: string; artifact_url: string; sha256: string; size_bytes: number; flash_offset: number; release_notes: string | null };
type InstallerLog = { text: string; tone?: "good" | "bad" };

async function sha256Hex(bytes: Uint8Array) {
  const digest = await crypto.subtle.digest("SHA-256", bytes.buffer as ArrayBuffer);
  return Array.from(new Uint8Array(digest)).map(value => value.toString(16).padStart(2, "0")).join("");
}

export default function GuestInstaller() {
  const [release, setRelease] = useState<PublicRelease | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "empty" | "error">("loading");
  const [deviceId, setDeviceId] = useState("SENSABLE-01");
  const [wifiSsid, setWifiSsid] = useState("");
  const [wifiPassword, setWifiPassword] = useState("");
  const [flashing, setFlashing] = useState(false);
  const [logs, setLogs] = useState<InstallerLog[]>([]);
  const serialSupported = typeof window !== "undefined" && Boolean(navigator.serial) && window.isSecureContext;
  const origin = window.location.origin;
  const log = (text: string, tone?: InstallerLog["tone"]) => setLogs(previous => [...previous, { text, tone }]);

  useEffect(() => {
    fetch("/api/public/installer/latest")
      .then(async response => ({ response, body: await response.json() }))
      .then(({ response, body }) => {
        if (response.status === 404) return setState("empty");
        if (!response.ok || !body.release) return setState("error");
        setRelease(body.release); setState("ready");
      })
      .catch(() => setState("error"));
  }, []);

  const install = async () => {
    if (!release) return log("No approved firmware release is available yet.", "bad");
    if (!serialSupported) return log("Open this page in current Chrome or Edge over HTTPS to use USB flashing.", "bad");
    if (!/^[A-Z0-9][A-Z0-9_-]{2,47}$/.test(deviceId.trim().toUpperCase())) return log("Device ID must use A-Z, 0-9, _ or - and be 3–48 characters.", "bad");
    if (!wifiSsid || !wifiPassword) return log("Enter Wi-Fi SSID and password. They stay only in this browser and ESP32.", "bad");
    setFlashing(true); setLogs([]);
    let port: SerialPort | undefined;
    try {
      log("Downloading approved firmware…");
      const artifactResponse = await fetch(release.artifact_url);
      if (!artifactResponse.ok) throw new Error("approved_firmware_download_failed");
      const binary = new Uint8Array(await artifactResponse.arrayBuffer());
      const checksum = await sha256Hex(binary);
      if (checksum !== release.sha256) throw new Error("firmware_checksum_mismatch");
      log("Firmware SHA-256 verified. Choose your ESP32 port.");
      port = await navigator.serial!.requestPort();
      const transport = new Transport(port as never, true);
      const loader = new ESPLoader({ transport, baudrate: 115200, terminal: { clean: () => undefined, write: data => log(String(data)), writeLine: data => log(String(data)) } });
      const chip = await loader.main();
      log(`Connected to ${chip}. Flashing ${release.version}…`);
      await loader.writeFlash({ fileArray: [{ data: binary, address: release.flash_offset }], flashMode: "dio" as never, flashFreq: "40m" as never, flashSize: "4MB" as never, eraseAll: false, compress: true, reportProgress: (_index, written, total) => log(`Flash progress: ${Math.round((written / total) * 100)}%`) });
      await loader.after("hard_reset");
      log("Firmware written. The board is rebooting.", "good");

      log("Creating a one-time local device credential…");
      const enrollment = await fetch("/api/public/installer/enroll", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ device_id: deviceId.trim().toUpperCase() }) });
      const enrollmentBody = await enrollment.json();
      if (!enrollment.ok || !enrollmentBody.device_token) throw new Error(enrollmentBody.code || "device_enrollment_failed");

      log("Choose the ESP32 port once more to write Wi-Fi and gateway configuration locally.");
      const configPort = await navigator.serial!.requestPort();
      await configPort.open({ baudRate: 115200 });
      const writer = configPort.writable?.getWriter();
      if (!writer) throw new Error("serial_writer_unavailable");
      const command = `CONFIG|${wifiSsid}|${wifiPassword}|${origin}|${deviceId.trim().toUpperCase()}|${enrollmentBody.device_token}\n`;
      await writer.write(new TextEncoder().encode(command));
      writer.releaseLock(); await configPort.close();
      setWifiSsid("");
      setWifiPassword("");
      log("Local configuration sent. Wait for the ESP32 serial log to show GATEWAY_CONFIG_SAVED, then verify a test-signal heartbeat with the project owner.", "good");
    } catch (error) {
      log(`Installer stopped: ${error instanceof Error ? error.message : "unknown_error"}`, "bad");
    } finally {
      setFlashing(false);
      try { await port?.close(); } catch { /* The serial port may already be closed by esptool. */ }
    }
  };

  return <div className="blueprint-grid min-h-screen text-slate-100"><header className="border-b border-cyan-100/15 bg-[#061a44]/90 px-5 py-4 backdrop-blur md:px-10"><div className="mx-auto flex max-w-6xl items-center justify-between"><div><p className="blueprint-label">SENS-Able</p><p className="font-semibold text-white">ESP32 Guest Installer</p></div><div className="flex items-center gap-2 text-xs text-emerald-100"><ShieldCheck className="h-4 w-4" /> Approved firmware only</div></div></header><main className="mx-auto max-w-6xl px-5 py-10 md:px-10"><section className="cad-frame relative overflow-hidden p-7 md:p-10"><div className="absolute -right-20 -top-20 h-72 w-72 rounded-full border border-cyan-200/15"/><p className="blueprint-label">No-login USB deployment</p><h1 className="mt-4 max-w-3xl text-4xl font-extrabold tracking-tight text-white md:text-5xl">Flash SENS-Able to an ESP32 from your browser.</h1><p className="mt-5 max-w-3xl text-base leading-8 text-slate-300">Connect the ESP32 by USB, use Chrome or Edge, and approve the port picker. The installer can write only the latest approved firmware release. It cannot access USB, Wi-Fi, or your device without your explicit browser permissions.</p></section><section className="mt-7 grid gap-6 lg:grid-cols-[1.05fr_0.95fr]"><article className="cad-frame p-6"><div className="flex items-center gap-3"><Download className="h-5 w-5 text-cyan-100"/><div><p className="blueprint-label">Approved release</p><h2 className="font-semibold text-white">{state === "ready" ? `${release?.version} · ${release?.board}` : state === "loading" ? "Checking gateway…" : state === "empty" ? "No release registered" : "Gateway unavailable"}</h2></div></div>{release ? <div className="mt-5 space-y-3 text-sm text-slate-300"><p>{release.release_notes || "No release notes provided."}</p><p className="font-mono text-xs text-cyan-100">SHA-256: {release.sha256}</p><p>{(release.size_bytes / 1024).toFixed(1)} KB · Flash offset 0x{release.flash_offset.toString(16)}</p></div> : <p className="mt-5 text-sm leading-7 text-slate-400">The project owner must register a compiled firmware artifact before guest USB installation becomes available.</p>}<div className="mt-6 flex items-center gap-2 text-sm">{serialSupported ? <><CheckCircle2 className="h-4 w-4 text-emerald-300"/> <span className="text-emerald-100">Web Serial is available.</span></> : <><CircleAlert className="h-4 w-4 text-amber-200"/> <span className="text-amber-100">Use Chrome or Edge over HTTPS.</span></>}</div></article><article className="cad-frame p-6"><div className="flex items-center gap-3"><Wifi className="h-5 w-5 text-cyan-100"/><div><p className="blueprint-label">Local provisioning</p><h2 className="font-semibold text-white">Connect the newly flashed device</h2></div></div><p className="mt-4 text-sm leading-7 text-slate-300">Wi-Fi credentials and a new device token are sent only from this browser to your chosen ESP32 port. This page does not display, save, or list the token after configuration.</p><div className="mt-5 space-y-3"><Input value={deviceId} onChange={event => setDeviceId(event.target.value.toUpperCase())} placeholder="SENSABLE-01" className="border-cyan-100/25 bg-[#031337] text-white"/><Input value={wifiSsid} onChange={event => setWifiSsid(event.target.value)} placeholder="Wi-Fi network name" className="border-cyan-100/25 bg-[#031337] text-white"/><Input value={wifiPassword} onChange={event => setWifiPassword(event.target.value)} type="password" placeholder="Wi-Fi password" className="border-cyan-100/25 bg-[#031337] text-white"/></div><Button disabled={flashing || !release || !serialSupported} onClick={install} className="mt-6 w-full bg-cyan-300 text-blue-950 hover:bg-cyan-200">{flashing ? <><Loader2 className="mr-2 h-4 w-4 animate-spin"/> Installing…</> : <><PlugZap className="mr-2 h-4 w-4"/> Choose ESP32 and install</>}</Button><p className="mt-4 text-xs leading-5 text-slate-400">This is a technical installer. It does not validate a glucose model, create clinical results, or collect participant identity data.</p></article></section><section className="cad-frame mt-7 p-6"><p className="blueprint-label">Before first live report</p><div className="mt-4 grid gap-4 md:grid-cols-3"><div><p className="font-semibold text-white">1. Publish the gateway</p><p className="mt-1 text-sm leading-6 text-slate-300">The owner clicks Publish so the browser installer has its final HTTPS domain.</p></div><div><p className="font-semibold text-white">2. Flash by USB</p><p className="mt-1 text-sm leading-6 text-slate-300">Use the button above, choose the ESP32 port twice, and keep the USB cable connected until setup finishes.</p></div><div><p className="font-semibold text-white">3. Use certificate-aware release</p><p className="mt-1 text-sm leading-6 text-slate-300">v0.7.1 can flash and provision. A later root-CA release is required before it can send live HTTPS test readings.</p></div></div></section><section className="cad-frame mt-7 p-6"><p className="blueprint-label">Installer activity</p><div className="mt-4 space-y-2">{logs.length ? logs.map((entry, index)=><p key={`${entry.text}-${index}`} className={`border-l-2 px-3 py-2 font-mono text-xs ${entry.tone === "good" ? "border-emerald-300 text-emerald-100" : entry.tone === "bad" ? "border-red-300 text-red-100" : "border-cyan-200/40 text-slate-200"}`}>{entry.text}</p>) : <p className="text-sm text-slate-400">Installation progress and browser/serial errors will appear here.</p>}</div></section><section className="mt-6 flex items-start gap-3 border border-cyan-100/20 bg-cyan-100/5 p-5 text-sm leading-7 text-slate-300"><LockKeyhole className="mt-1 h-5 w-5 shrink-0 text-cyan-100"/><p><strong className="text-white">Privacy boundary:</strong> The public installer exposes release version and checksum only. It never shows dashboard readings, prior devices, owner reports, or existing device tokens. The owner dashboard remains separate for release upload and research evidence.</p></section></main></div>;
}
