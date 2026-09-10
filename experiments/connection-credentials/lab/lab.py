#!/usr/bin/env python3
"""
Reproducible lab for the credentials / socket-pool experiment.

Coldness guarantee: every run is served on a PORT THAT HAS NEVER BEEN USED BEFORE.
Chrome keys its socket pools on (scheme, host, port), so a virgin port cannot have a
warm connection - in any browser, with no harness tricks. Each page also self-checks
(`valid`) and refuses to report a run where the document reused a connection.

  backend : HTTPS (self-signed) on 127.0.0.1:8901
  relays  : plain TCP on 127.0.0.1:PORT_LO..PORT_HI, each delaying every chunk by
            RTT/2 in each direction, so TLS and the request/response cost a real RTT.

Variants (?v=N, optional &gap=MS for a hydration stall before the fetch):
  1  fetch ajax, credentials:"omit"                        (no hints)
  2  <link rel=preconnect crossorigin> + fetch omit
  3  <link rel=preload as=fetch crossorigin> + fetch omit
  4  fetch ajax, credentials:"same-origin"                 (with credentials)
"""
import asyncio, ssl, threading, time, json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BACKEND = 8901
PORT_LO, PORT_HI = 8902, 8991     # 90 virgin ports
import threading as _t
NEXT_PORT = PORT_LO
PORT_LOCK = _t.Lock()
RTT_MS = 120.0
HALF = RTT_MS / 2000.0

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>variant %(n)s</title>
%(hint)s
<style>
 body{margin:0;font:15px system-ui,sans-serif;background:#0c1116;color:#e8eef4}
 .w{max-width:44rem;margin:0 auto;padding:2rem 1.25rem}
 h1{font-size:.8125rem;letter-spacing:.06em;text-transform:uppercase;color:#8895a5;margin:0 0 1rem}
 #slot{min-height:380px;display:flex;align-items:center;justify-content:center;
       border:1px dashed #37424f;border-radius:10px;color:#8895a5;font-size:.8125rem}
 .lcp{width:100%%;min-height:380px;display:flex;flex-direction:column;justify-content:center;
      padding:3rem 2rem;border-radius:10px;color:#fff;
      background:linear-gradient(135deg,#1c3f5e,#3d6d94)}
 .lcp h2{margin:0;font-size:clamp(2.4rem,7vw,4.2rem);line-height:1.02;letter-spacing:-.03em}
 .lcp p{margin:.9rem 0 0;font-size:1rem;opacity:.8}
 .readout{margin:1rem 0 .6rem;font-size:1.05rem;font-weight:700;
          font-family:ui-monospace,Menlo,monospace;color:#f0972f}
 .readout span{color:#8895a5;font-weight:400;font-size:.8125rem;margin-left:.5rem}
 pre{font-size:.7rem;line-height:1.45;color:#66717f;white-space:pre-wrap;margin:.8rem 0 0}
 .bad{background:#3a2a13;color:#f0972f;padding:.6rem .8rem;border-radius:6px;
      font-size:.8125rem;margin-bottom:1rem}
</style>
</head>
<body>
<div class="w">
  <h1>%(label)s &middot; port %(port)s</h1>
  <div id="warn"></div>
  <div id="slot">waiting for AJAX&hellip;</div>
  <div class="readout" id="readout"></div>
  <pre id="out"></pre>
</div>
<script>
(function(){
  var lcpTime = 0;
  try {
    new PerformanceObserver(function(list){
      var es = list.getEntries();
      lcpTime = es[es.length - 1].startTime;
    }).observe({type:'largest-contentful-paint', buffered:true});
  } catch(e){}

  var CREDS = %(creds)s, GAP = %(gap)s;

  function measure(){
    var all = performance.getEntriesByType('resource').filter(function(x){
      return x.name.indexOf('/ajax') !== -1;
    });
    var e = all[all.length - 1];
    var nav = performance.getEntriesByType('navigation')[0];
    var docConnect = Math.round(nav.connectEnd - nav.connectStart);

    var r = { variant:%(n)s, label:%(labelJson)s, port:%(port)s, creds:CREDS, gap:GAP,
              lcp:Math.round(lcpTime), docConnect:docConnect,
              docEnd:Math.round(nav.responseEnd), ajaxEntries:all.length,
              // A cold origin MUST pay for the document's own connection.
              valid: docConnect > 0 };
    if (e) {
      var tls = e.secureConnectionStart ? e.connectEnd - e.secureConnectionStart : 0;
      r.ajaxStart = Math.round(e.startTime);
      r.newSocket = e.connectEnd > e.connectStart;
      r.tcp   = Math.round(Math.max(0, e.connectEnd - e.connectStart - tls));
      r.tls   = Math.round(tls);
      r.setup = Math.round(e.connectEnd - e.connectStart);
      r.ttfb  = Math.round(e.responseStart - e.requestStart);
      r.ajaxEnd = Math.round(e.responseEnd);
    }
    if (!r.valid) {
      document.getElementById('warn').className = 'bad';
      document.getElementById('warn').textContent =
        'INVALID RUN - the document reused an existing connection, so this port was not cold. ' +
        'Reload on a fresh port.';
    }
    window.__result = r;
    document.getElementById('readout').innerHTML =
      'LCP ' + r.lcp + ' ms' +
      '<span>' + (r.newSocket ? 'COLD - this fetch opened its own socket (' + r.setup + ' ms setup)'
                              : 'WARM - reused the page connection (0 ms setup)') + '</span>';
    document.getElementById('out').textContent = JSON.stringify(r, null, 1);
    if (window.parent !== window) window.parent.postMessage(r, '*');
    var back = new URLSearchParams(location.search).get('back');
    if (back) setTimeout(function(){
      location.href = back + '#' + encodeURIComponent(JSON.stringify(r));
    }, 900);
  }

  if (GAP) { var end = performance.now() + GAP; while (performance.now() < end) {} }

  fetch('/ajax', { credentials: CREDS, cache: 'no-store' })
    .then(function(res){ return res.json(); })
    .then(function(data){
      var slot = document.getElementById('slot');
      slot.style.border = 'none';
      slot.innerHTML = '<div class="lcp"><h2>' + data.headline +
        '</h2><p>Fetched over AJAX with credentials: ' + CREDS + '</p></div>';
      requestAnimationFrame(function(){ requestAnimationFrame(function(){
        setTimeout(measure, 60);
      });});
    });
})();
</script>
</body>
</html>
"""


RUNNER = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Four page loads, four cold connections</title>
<style>
:root{--bg:#f4f6f8;--card:#fff;--sunk:#eef1f5;--ink:#10151c;--ink2:#48535f;--muted:#6b7684;
--line:#dde3ea;--line2:#c6d0da;--cold:#d2740f;--warm:#128063;--tls:#6f52c9;--wait:#4b6b8a}
@media(prefers-color-scheme:dark){:root{--bg:#0c1116;--card:#141b22;--sunk:#1b232c;--ink:#e8eef4;
--ink2:#c2ccd8;--muted:#8895a5;--line:#232d38;--line2:#37424f;--cold:#f0972f;--warm:#3ec79b;
--tls:#a48df0;--wait:#8fb0cf}}
*{box-sizing:border-box}html{color-scheme:light dark}
body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.w{max-width:56rem;margin:0 auto;padding:2rem 1.15rem 3rem}
h1{font-size:1.5rem;letter-spacing:-.025em;margin:0 0 .4rem}
.sub{color:var(--ink2);margin:0 0 1.25rem;max-width:44rem}
button{font:600 13px/1 inherit;padding:.65rem .95rem;border-radius:6px;
border:1px solid var(--line2);background:var(--card);color:var(--ink);cursor:pointer}
button.go{background:var(--ink);color:var(--bg);border-color:var(--ink)}
button:disabled{opacity:.45;cursor:default}
:focus-visible{outline:2px solid var(--cold);outline-offset:2px}
.bar{display:flex;gap:.6rem;align-items:center;margin-bottom:1.1rem;flex-wrap:wrap}
.status{font-size:.8125rem;color:var(--muted);font-family:ui-monospace,Menlo,monospace}
.rows{display:flex;flex-direction:column;gap:.5rem}
.row{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:.8rem .9rem;
display:grid;grid-template-columns:auto 1fr auto;gap:.85rem;align-items:center}
.row.next{border-color:var(--cold)}
.idx{font-family:ui-monospace,monospace;color:var(--muted);font-size:.8125rem}
.name{font-weight:600;font-size:.9375rem}
.code{color:var(--muted);font-size:.72rem;margin-top:.12rem;font-family:ui-monospace,Menlo,monospace}
.res{text-align:right;white-space:nowrap}
.t{font-size:1.1rem;font-weight:700;font-variant-numeric:tabular-nums}
.badge{display:inline-block;font-size:.65rem;font-weight:700;padding:.08rem .4rem;
border-radius:3px;border:1px solid;margin-top:.2rem}
.b-cold{color:var(--cold);border-color:var(--cold)}
.b-warm{color:var(--warm);border-color:var(--warm)}
.track{grid-column:1/-1;height:16px;background:var(--sunk);border-radius:4px;display:flex;overflow:hidden}
.track i{height:100%}
.k-tls{background:var(--tls)}.k-wait{background:var(--wait)}.k-rest{background:var(--warm)}
.det{grid-column:1/-1;font-size:.7rem;color:var(--muted);font-family:ui-monospace,Menlo,monospace}
.link{grid-column:1/-1;display:flex;align-items:center;gap:.7rem;flex-wrap:wrap;
 margin-top:.2rem;padding-top:.65rem;border-top:1px dashed var(--line2)}
.link a{display:inline-block;background:var(--cold);color:#fff;text-decoration:none;
 font:700 13px/1 ui-sans-serif,system-ui,sans-serif;padding:.6rem .9rem;border-radius:6px;
 white-space:nowrap}
.link a:hover{filter:brightness(1.08)}
.link em{font-style:normal;color:var(--muted);font-size:.75rem;
 font-family:ui-monospace,Menlo,monospace}
.note{margin-top:1.25rem;font-size:.8125rem;color:var(--ink2);
border-left:2px solid var(--line2);padding-left:.9rem;display:flex;flex-direction:column;gap:.55rem}
.note b{color:var(--ink)}
</style></head><body><div class="w">

<h1>Four page loads, four cold connections</h1>
<p class="sub">Each variant is a real page load that fetches the LCP element over AJAX. Every load is
served on a <b>port that has never been used before</b>, so there is no socket left over from the
previous load to reuse &mdash; the connection is genuinely fresh every time. The browser navigates to
each variant in turn and comes back here with the numbers.</p>

<div class="bar">
  <button class="go" id="run">Run the four page loads</button>
  <button id="fresh">New ports</button>
  <button id="clear">Clear</button>
  <span class="status" id="status">ready</span>
</div>

<div class="rows" id="rows"></div>

<div class="note">
<p><b>COLD</b> means that fetch opened its own socket and paid a TCP + TLS handshake.
<b>WARM</b> means it reused the connection the page itself arrived on.</p>
<p>Variants 1&ndash;3 fetch with <code>credentials:"omit"</code>. Variant 4 fetches with credentials.
Same origin, same bytes, same everything else. A load whose own document reused a connection is
flagged INVALID &mdash; that port was not cold and the number cannot be trusted.</p>
</div>
</div>

<script>
var OPTS=[
 {v:1,name:"Fetch without credentials",code:'credentials:"omit" - no hints'},
 {v:2,name:"Preconnect crossorigin, then fetch without credentials",code:'<link rel=preconnect crossorigin> + credentials:"omit"'},
 {v:3,name:"Preload the AJAX, then fetch without credentials",code:'<link rel=preload as=fetch crossorigin> + credentials:"omit"'},
 {v:4,name:"Fetch with credentials",code:'credentials:"same-origin"'}
];
var KEY='cx-results';
function load(){ try{return JSON.parse(sessionStorage.getItem(KEY)||'{}');}catch(e){return {};} }
function save(r){ try{sessionStorage.setItem(KEY,JSON.stringify(r));}catch(e){} }
var results=load();

// A returning variant page carries its result in the hash.
if(location.hash.length>1){
  try{ var got=JSON.parse(decodeURIComponent(location.hash.slice(1)));
       if(got&&got.variant){ results[got.variant]=got; save(results); } }catch(e){}
  history.replaceState(null,'',location.pathname);
}

function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;');}
function el(t,c,h){var e=document.createElement(t);if(c)e.className=c;if(h!=null)e.innerHTML=h;return e;}
function nextVariant(){ for(var i=0;i<OPTS.length;i++){ if(!results[OPTS[i].v]) return OPTS[i].v; } return 0; }

var links={};
async function freshLinks(){
  var back=encodeURIComponent(location.origin+location.pathname);
  for(var i=0;i<OPTS.length;i++){
    var p=await (await fetch('/port',{cache:'no-store'})).json();
    links[OPTS[i].v]={port:p.port,
      url:'https://localhost:'+p.port+'/?v='+OPTS[i].v+'&back='+back};
  }
  draw();
}

function draw(){
  var rowsEl=document.getElementById('rows'); rowsEl.textContent='';
  var nx=nextVariant(), max=1;
  OPTS.forEach(function(o){var r=results[o.v];if(r&&r.lcp>max)max=r.lcp;});
  OPTS.forEach(function(o){
    var r=results[o.v],row=el('div','row'+(nx===o.v?' next':''));
    row.appendChild(el('div','idx',String(o.v)));
    var mid=el('div');
    mid.appendChild(el('div','name',esc(o.name)));
    mid.appendChild(el('div','code',esc(o.code)));
    row.appendChild(mid);
    var right=el('div','res');
    if(r){
      right.appendChild(el('div','t',r.lcp+' ms'));
      right.appendChild(el('span','badge '+(r.newSocket?'b-cold':'b-warm'),r.newSocket?'COLD':'WARM'));
    } else right.appendChild(el('div','t',nx===o.v?'next':'-'));
    row.appendChild(right);
    if(r){
      var tr=el('div','track');
      [['k-tls',r.setup],['k-wait',r.ttfb],['k-rest',Math.max(0,r.lcp-r.ajaxStart-r.setup-r.ttfb)]]
      .forEach(function(p){if(p[1]>0){var i=el('i',p[0]);i.style.width=(p[1]/max*100)+'%';tr.appendChild(i);}});
      row.appendChild(tr);
      row.appendChild(el('div','det',
        'port '+r.port+' &middot; doc connect '+r.docConnect+' ms &middot; ajax starts '+r.ajaxStart+
        ' ms &middot; setup '+r.setup+' ms (tls '+r.tls+') &middot; ttfb '+r.ttfb+' ms &middot; '+
        r.ajaxEntries+' ajax entr'+(r.ajaxEntries===1?'y':'ies')+
        (r.valid?'':' &middot; INVALID: document reused a connection')));
    }
    var lk=links[o.v];
    if(lk){
      var ld=el('div','link');
      ld.innerHTML='<a href="'+lk.url+'">Open variant '+o.v+' &rarr; port '+lk.port+'</a>'+
        '<em>virgin port - this load gets a guaranteed fresh connection</em>';
      row.appendChild(ld);
    }
    rowsEl.appendChild(row);
  });
  var s=document.getElementById('status');
  s.textContent = nx ? ('next: variant '+nx) : 'all four done - each on its own fresh port';
  document.getElementById('run').textContent = nx===1 ? 'Run the four page loads' :
    (nx ? ('Continue with variant '+nx) : 'Run again');
}

async function step(){
  var nx=nextVariant();
  if(!nx){ results={}; save(results); nx=1; draw(); }
  document.getElementById('status').textContent='variant '+nx+': claiming a virgin port...';
  var p=await (await fetch('/port',{cache:'no-store'})).json();
  var back=encodeURIComponent(location.origin+location.pathname);
  location.href='https://localhost:'+p.port+'/?v='+nx+'&back='+back;
}

document.getElementById('run').addEventListener('click',step);
document.getElementById('clear').addEventListener('click',function(){
  results={}; save(results); freshLinks();
});
document.getElementById('fresh').addEventListener('click',freshLinks);

draw();
freshLinks();
// Chain automatically while a run is in progress.
if(nextVariant()>1) setTimeout(step,700);
</script>
</body></html>
"""

CREDS = {1: '"omit"', 2: '"omit"', 3: '"omit"', 4: '"same-origin"'}
LABELS = {
    1: "1 - fetch without credentials, no hints",
    2: "2 - preconnect crossorigin + fetch without credentials",
    3: "3 - preload as=fetch crossorigin + fetch without credentials",
    4: "4 - fetch with credentials (reuses the document connection)",
}


def hint(n, origin):
    if n == 2:
        return '<link rel="preconnect" href="%s" crossorigin>' % origin
    if n == 3:
        return '<link rel="preload" as="fetch" crossorigin href="/ajax">'
    return ""


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _send(self, body, ctype, extra=None):
        b = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        parts = self.path.split("?")
        path, qs = parts[0], (parts[1] if len(parts) > 1 else "")
        q = dict(p.split("=", 1) for p in qs.split("&") if "=" in p)
        host = self.headers.get("Host", "localhost:%d" % PORT_LO)
        port = host.rsplit(":", 1)[-1]
        origin = "https://" + host

        if path == "/port":
            global NEXT_PORT
            with PORT_LOCK:
                NEXT_PORT += 1
                p = NEXT_PORT
            self._send(json.dumps({"port": p}), "application/json",
                       {"Access-Control-Allow-Origin": "*"})
            return
        if path == "/runner":
            self._send(RUNNER, "text/html; charset=utf-8")
            return
        if path == "/ajax":
            self._send(json.dumps({"headline": "This block is the LCP element"}),
                       "application/json",
                       {"Timing-Allow-Origin": "*", "Access-Control-Allow-Origin": "*"})
            return
        if path == "/":
            n = int(q.get("v", 1))
            gap = int(q.get("gap", 0))
            self._send(PAGE % {
                "n": n, "hint": hint(n, origin), "creds": CREDS[n], "gap": gap,
                "label": LABELS[n], "labelJson": json.dumps(LABELS[n]), "port": port,
            }, "text/html; charset=utf-8")
            return
        self.send_response(404)
        self.send_header("Content-Length", "0")
        self.end_headers()


async def pump(reader, writer):
    try:
        while True:
            chunk = await reader.read(65536)
            if not chunk:
                break
            await asyncio.sleep(HALF)
            writer.write(chunk)
            await writer.drain()
    except Exception:
        pass
    finally:
        try:
            writer.close()
        except Exception:
            pass


async def handle(cr, cw):
    try:
        sr, sw = await asyncio.open_connection("127.0.0.1", BACKEND)
    except Exception:
        cw.close()
        return
    await asyncio.gather(pump(cr, sw), pump(sr, cw))


async def relays():
    servers = []
    for p in range(PORT_LO, PORT_HI + 1):
        servers.append(await asyncio.start_server(handle, "127.0.0.1", p))
    print("lab up: https://localhost:{%d..%d}/?v=1..4  (RTT %dms)"
          % (PORT_LO, PORT_HI, RTT_MS), flush=True)
    await asyncio.gather(*[s.serve_forever() for s in servers])


def backend():
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain("cert.pem", "key.pem")
    httpd = ThreadingHTTPServer(("127.0.0.1", BACKEND), H)
    httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)
    httpd.serve_forever()


if __name__ == "__main__":
    threading.Thread(target=backend, daemon=True).start()
    time.sleep(0.4)
    asyncio.run(relays())
