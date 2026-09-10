#!/usr/bin/env bash
# One command. Starts the lab and opens it in a throwaway browser.
set -euo pipefail
cd "$(dirname "$0")"

[ -f cert.pem ] || openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem \
  -days 90 -nodes -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" 2>/dev/null

pgrep -f "python3 lab.py" >/dev/null || {
  setsid nohup python3 lab.py > lab.log 2>&1 < /dev/null &
  sleep 4
}

URL="https://localhost:8902/runner"

CHROME=""
for c in google-chrome google-chrome-stable chromium chromium-browser \
         "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"; do
  command -v "$c" >/dev/null 2>&1 && { CHROME="$c"; break; }
  [ -x "$c" ] && { CHROME="$c"; break; }
done

if [ -n "$CHROME" ]; then
  echo "Opening $URL"
  # Throwaway profile - your normal Chrome and its settings are untouched.
  # --ignore-certificate-errors is needed because the lab's cert is self-signed;
  # TLS is what makes the handshake cost measurable, so it cannot be dropped.
  nohup "$CHROME" --user-data-dir=/tmp/cx-demo --ignore-certificate-errors \
    --no-first-run --no-default-browser-check "$URL" > /dev/null 2>&1 &
  sleep 1
  echo "Done. If nothing opened, see the note below."
else
  echo "No Chrome found. Open $URL yourself in a browser started with:"
  echo "  --user-data-dir=/tmp/cx-demo --ignore-certificate-errors"
fi

cat <<'NOTE'

Why a throwaway browser: the lab serves HTTPS with a self-signed certificate.
TLS is the point - the handshake is the cost being measured, and over plain HTTP
on loopback a new connection costs ~0ms, so there would be nothing to see.
Your everyday Chrome profile is not touched; the demo runs in /tmp/cx-demo.

./stop.sh shuts the lab down.
NOTE
