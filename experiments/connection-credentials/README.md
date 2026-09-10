# The fetch that pays for its own handshake

A same-origin `fetch()` can be structurally incapable of reusing the connection your page arrived
on. One option does it: `credentials: "omit"`.

**Live demo:** https://corewebvitals.github.io/pagespeed/experiments/connection-credentials/

## What is going on

Chromium tags a request made with `credentials: "omit"` as **privacy mode** — no cookies, no client
certificates, no cached credentials. Privacy mode is a field in:

- `ClientSocketPool::GroupId` — which pool of sockets a request may draw from
- `SpdySessionKey` — which HTTP/2 session it may join
- `QuicSessionKey` — the same on HTTP/3

So an uncredentialed request cannot join the session carrying your document, your CSS and your JS.
Same host, same scheme, same port, and it still has to open a second socket and pay for a TCP + TLS
handshake before it can do anything.

If the response it is waiting for contains your LCP element, that handshake is on the critical path.

## The four variants

| # | Variant | Result |
|---|---|---|
| 1 | `fetch(url, {credentials:"omit"})`, no hints | COLD — opens its own socket |
| 2 | `<link rel="preconnect" crossorigin>` then `credentials:"omit"` | COLD — still opens its own socket |
| 3 | `<link rel="preload" as="fetch" crossorigin>` then `credentials:"omit"` | COLD — still opens its own socket |
| 4 | `fetch(url, {credentials:"same-origin"})` | WARM — reuses the document connection |

Measured locally over an emulated 120 ms RTT, five cold runs each:

| Variant | LCP (median) | vs 1 | New socket | Setup |
|---|---|---|---|---|
| 1 | 744 ms | — | 5/5 | 124 ms |
| 2 | 740 ms | −4 ms | 5/5 | 124 ms |
| 3 | 744 ms | +0 ms | 5/5 | 123 ms |
| 4 | **512 ms** | **−232 ms** | 0/5 | 0 ms |

Adding a 1000 ms hydration stall before the fetch moved every number up by 1000 ms and changed
nothing else — variant 4 still won by ~240 ms, variants 2 and 3 still gained nothing.

**The preconnect result is the surprise.** The common advice is that
`<link rel="preconnect" crossorigin>` warms the anonymous pool and takes the handshake off the
critical path. In this setup it does not, not even with a full second of headroom. Variant 3 shows
the preload definitely fired (two `/ajax` timing entries) and the fetch still opened its own socket.

## Why the live demo is limited

GitHub Pages is one origin on port 443. Chrome keys socket pools on (scheme, host, port), so the
first uncredentialed request opens a socket and every later one reuses it. You get **one cold
reading per pool per browser session** — reopen the page in a private window to test cold again.
The page labels every run COLD or WARM so a warm socket can never be misread as a win.

## The real experiment

`lab/` runs it properly: four real page loads, each served on a **port that has never been used
before**, so no socket can survive from the previous load.

    cd lab
    ./start.sh

Then open the runner in a Chrome that tolerates the self-signed cert:

    google-chrome --user-data-dir=/tmp/cx-demo --ignore-certificate-errors \
      https://localhost:8902/runner

The runner gives you a link per variant on a fresh port, or chains all four automatically.
`./stop.sh` shuts it down.

Headless batch runs:

    ROUNDS=5 GAP=0 PORT_LO=8902 node run.mjs > res_nogap.json
    python3 report.py report.html

(needs `google-chrome --headless=new --remote-debugging-port=9333 --ignore-certificate-errors`)

### How the lab works

- HTTPS backend on 8901, plus 90 TCP relays on 8902–8991. Each relay delays every chunk by RTT/2 in
  each direction, so the TLS handshake and the request/response each cost a real round trip.
- Coldness comes from the virgin port — no browser flags, no profile tricks, works anywhere.
- Every page self-validates: a cold origin *must* pay for its own document connection, so
  `docConnect === 0` marks the run INVALID and it is excluded.

### Known limits

- **TCP reads 0 ms.** The browser's TCP handshake completes against the local relay over loopback;
  only the bytes after it carry the emulated delay. On a real network TCP costs another round trip,
  so real setup cost is roughly double what the lab shows.
- **HTTP/1.1, not HTTP/2.** HTTP/1.1 pools up to six connections per origin and binds them
  differently. Variant 4's result holds either way, but the null result for variants 2 and 3 may not
  transfer to an h2 origin.

## If you hit this in production

Do not just delete `credentials: "omit"` — it is often there to keep responses cacheable at the CDN
without cookies in the cache key. Check the cache policy first: if it forwards cookies, removing the
flag makes the key per-user and the hit rate collapses, which costs far more than two round trips.
