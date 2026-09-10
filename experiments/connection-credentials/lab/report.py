#!/usr/bin/env python3
"""Render measured results into a standalone report page."""
import json, statistics as st, datetime, html, sys, os

OUT = sys.argv[1] if len(sys.argv) > 1 else "report.html"

CONFIGS = [("No gap — fetch fires as soon as the page parses", "res_nogap.json"),
           ("1000 ms hydration gap before the fetch", "res_gap.json")]

NAMES = {
    1: ("Fetch without credentials", 'credentials:"omit"; no resource hints'),
    2: ("Preconnect crossorigin + fetch without credentials",
        '&lt;link rel="preconnect" crossorigin&gt; in head'),
    3: ("Preload as=fetch crossorigin + fetch without credentials",
        '&lt;link rel="preload" as="fetch" crossorigin&gt; in head'),
    4: ("Fetch with credentials", 'credentials:"same-origin" — reuses the document connection'),
}


def block(title, path):
    if not os.path.exists(path):
        return ""
    d = json.load(open(path))
    runs = d["runs"]
    invalid = [r for r in runs if not r.get("valid")]
    med, rows = {}, []
    for v in (1, 2, 3, 4):
        rs = [r for r in runs if r["variant"] == v and r.get("valid")]
        if not rs:
            continue
        med[v] = st.median([r["lcp"] for r in rs])
    worst = max(med.values()) if med else 1
    for v in (1, 2, 3, 4):
        rs = [r for r in runs if r["variant"] == v and r.get("valid")]
        if not rs:
            continue
        lcps = [r["lcp"] for r in rs]
        new = sum(1 for r in rs if r.get("newSocket"))
        setup = st.median([r.get("setup", 0) for r in rs])
        delta = med[v] - med[1]
        best = med[v] == min(med.values())
        rows.append(f"""
        <tr class="{'best' if best else ''}">
          <td class="v">{v}</td>
          <td><b>{NAMES[v][0]}</b><span class="hint">{NAMES[v][1]}</span></td>
          <td class="bar"><i style="width:{med[v] / worst * 100:.1f}%"></i></td>
          <td class="n big">{med[v]:.0f}<span class="u">ms</span></td>
          <td class="n {'good' if delta < 0 else 'flat'}">{'—' if v == 1 else f'{delta:+.0f} ms'}</td>
          <td class="n">{new}/{len(rs)}</td>
          <td class="n">{setup:.0f} ms</td>
          <td class="runs">{', '.join(str(x) for x in lcps)}</td>
        </tr>""")
    return f"""
    <section>
      <h2>{html.escape(title)}</h2>
      <p class="meta">{len(runs)} page loads &middot; {len(invalid)} invalid &middot;
         ports {min(r['port'] for r in runs)}–{max(r['port'] for r in runs)} &middot;
         emulated RTT {d.get('rtt', 120)} ms</p>
      <div class="scroll"><table>
        <thead><tr>
          <th></th><th>Variant</th><th>LCP</th><th class="n">Median</th><th class="n">vs 1</th>
          <th class="n">New socket</th><th class="n">Setup</th><th>All runs (ms)</th>
        </tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table></div>
    </section>"""


body = "".join(block(t, p) for t, p in CONFIGS)
stamp = datetime.datetime.now().strftime("%d %b %Y, %H:%M")

open(OUT, "w").write(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>LCP By Credentials Mode</title>
<style>
:root{{--bg:#f4f6f8;--card:#fff;--ink:#10151c;--ink2:#48535f;--muted:#6b7684;
--line:#dde3ea;--line2:#c6d0da;--bad:#d2740f;--good:#128063;--accent:#4b6b8a}}
@media(prefers-color-scheme:dark){{:root{{--bg:#0c1116;--card:#141b22;--ink:#e8eef4;
--ink2:#c2ccd8;--muted:#8895a5;--line:#232d38;--line2:#37424f;--bad:#f0972f;--good:#3ec79b;--accent:#8fb0cf}}}}
*{{box-sizing:border-box}} html{{color-scheme:light dark}}
body{{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
.w{{max-width:62rem;margin:0 auto;padding:2.5rem 1.25rem 4rem}}
h1{{font-size:1.6rem;letter-spacing:-.025em;margin:0 0 .4rem}}
h2{{font-size:1rem;margin:0 0 .25rem}}
.sub{{color:var(--ink2);margin:0 0 2rem;max-width:46rem}}
section{{background:var(--card);border:1px solid var(--line);border-radius:10px;
padding:1.1rem 1.15rem;margin-bottom:1.25rem}}
.meta{{color:var(--muted);font-size:.75rem;margin:0 0 .9rem;
font-family:ui-monospace,Menlo,monospace}}
.scroll{{overflow-x:auto}}
table{{border-collapse:collapse;width:100%;min-width:52rem;font-size:.8125rem}}
th{{text-align:left;font-size:.6875rem;letter-spacing:.07em;text-transform:uppercase;
color:var(--muted);font-weight:600;padding:0 .6rem .5rem 0;border-bottom:1px solid var(--line2)}}
td{{padding:.55rem .6rem .55rem 0;border-bottom:1px solid var(--line);vertical-align:middle}}
tr:last-child td{{border-bottom:0}}
tr.best td{{background:color-mix(in srgb,var(--good) 8%,transparent)}}
.v{{color:var(--muted);font-family:ui-monospace,monospace;width:1.5rem}}
.hint{{display:block;color:var(--muted);font-size:.75rem;font-weight:400;margin-top:.1rem}}
.n{{text-align:right;font-family:ui-monospace,Menlo,monospace;font-variant-numeric:tabular-nums;white-space:nowrap}}
.big{{font-size:1.05rem;font-weight:700}}
.u{{font-size:.7rem;color:var(--muted);margin-left:.15rem}}
.good{{color:var(--good);font-weight:700}} .flat{{color:var(--muted)}}
.bar{{width:26%;min-width:7rem}}
td:nth-child(2){{min-width:19rem}}
.bar i{{display:block;height:16px;border-radius:3px;background:var(--accent)}}
tr.best .bar i{{background:var(--good)}}
.runs{{color:var(--muted);font-family:ui-monospace,monospace;font-size:.7rem;white-space:nowrap}}
.notes{{font-size:.8125rem;color:var(--ink2);border-left:2px solid var(--line2);
padding-left:1rem;display:flex;flex-direction:column;gap:.7rem;max-width:46rem}}
.notes b{{color:var(--ink)}}
code{{font-family:ui-monospace,Menlo,monospace;font-size:.85em;background:var(--bg);
border:1px solid var(--line);border-radius:3px;padding:.05em .3em}}
</style></head><body><div class="w">

<h1>LCP by credentials mode</h1>
<p class="sub">Four ways of fetching the AJAX payload that contains the LCP element.
Every row is a full page load on a <b>port that has never been used before</b>, so the socket
pool is guaranteed cold — no warm connection can leak in from a previous run. Any load whose
document reused a connection is rejected as invalid and excluded.</p>

{body}

<div class="notes">
<p><b>What the data says.</b> Only variant 4 moves LCP. Reusing the document's connection saves
about 230 ms — one full handshake. Neither the preconnect nor the preload changed anything:
both still opened a new socket on 5 of 5 runs and still paid the same ~123 ms of TLS.</p>

<p><b>This contradicts the fix I proposed earlier.</b> I said
<code>&lt;link rel="preconnect" crossorigin&gt;</code> would warm the anonymous pool and take the
handshake off the critical path. In this lab it does not — not even with a 1000 ms gap between
parse and fetch, which is more headroom than the hint needs. Variant 3 shows the preload
definitely fired (two <code>/ajax</code> timing entries) and the subsequent fetch still opened its
own socket. Treat the preconnect advice as unproven until it is measured on the real stack.</p>

<p><b>Known limits of this rig.</b> TCP shows 0 ms in every variant: the browser's TCP handshake
completes against a local relay over loopback, and only the bytes after it carry the emulated
delay. On a real network TCP costs another round trip, so real setup is roughly double what is
shown here. The backend is HTTP/1.1, not HTTP/2 — the direction of the variant-4 result holds
either way, but HTTP/1.1 pools up to six connections per origin and binds them differently, so
the null result for variants 2 and 3 may not transfer to an h2 origin.</p>

<p><b>Reproduce.</b> <code>./run.sh</code> — starts the lab, launches a throwaway headless Chrome,
runs every variant on fresh ports, and regenerates this page. Generated {stamp}.</p>
</div>

</div></body></html>
""")
print("wrote", OUT)
