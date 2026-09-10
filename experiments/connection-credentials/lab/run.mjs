// Drives a throwaway headless Chrome over CDP.
// Coldness comes from the VIRGIN PORT per run; the fresh browser context is belt-and-braces.

const PORT = Number(process.env.CDP_PORT || 9333);
const ROUNDS = Number(process.env.ROUNDS || 5);
const GAP = Number(process.env.GAP || 0);
const PORT_LO = Number(process.env.PORT_LO || 8902);

const ver = await (await fetch(`http://127.0.0.1:${PORT}/json/version`)).json();
const ws = new WebSocket(ver.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });

let nextId = 1;
const pending = new Map();
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) {
    const { resolve, reject } = pending.get(m.id);
    pending.delete(m.id);
    m.error ? reject(new Error(JSON.stringify(m.error))) : resolve(m.result);
  }
};
function send(method, params = {}, sessionId) {
  const id = nextId++;
  ws.send(JSON.stringify(sessionId ? { id, method, params, sessionId } : { id, method, params }));
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject });
    setTimeout(() => { if (pending.delete(id)) reject(new Error(method + " timed out")); }, 30000);
  });
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function runOnce(variant, port) {
  const { browserContextId } = await send("Target.createBrowserContext", {});
  const { targetId } = await send("Target.createTarget", { url: "about:blank", browserContextId });
  const { sessionId } = await send("Target.attachToTarget", { targetId, flatten: true });
  await send("Page.enable", {}, sessionId);
  await send("Runtime.enable", {}, sessionId);

  const url = `https://localhost:${port}/?v=${variant}${GAP ? `&gap=${GAP}` : ""}`;
  await send("Page.navigate", { url }, sessionId);

  let out = null;
  const deadline = Date.now() + 25000;
  while (Date.now() < deadline) {
    await sleep(150);
    const r = await send("Runtime.evaluate", {
      expression: "window.__result ? JSON.stringify(window.__result) : null",
      returnByValue: true,
    }, sessionId);
    if (r.result && r.result.value) { out = JSON.parse(r.result.value); break; }
  }
  await send("Target.closeTarget", { targetId });
  await send("Target.disposeBrowserContext", { browserContextId });
  return out;
}

const all = [];
let portCursor = PORT_LO;
for (let round = 1; round <= ROUNDS; round++) {
  for (const v of [1, 2, 3, 4]) {
    const port = portCursor++;           // never reuse a port
    const r = await runOnce(v, port);
    if (r) { r.round = round; all.push(r); }
    else all.push({ variant: v, round, port, error: "no result", valid: false });
  }
}

console.log(JSON.stringify({ rtt: 120, gap: GAP, runs: all }, null, 1));
ws.close();
process.exit(0);
