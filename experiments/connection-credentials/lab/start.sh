#!/usr/bin/env bash
# Start the lab, then open the runner page.
set -euo pipefail
cd "$(dirname "$0")"

[ -f cert.pem ] || openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem \
  -days 90 -nodes -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" 2>/dev/null

pgrep -f "python3 lab.py" >/dev/null || {
  setsid nohup python3 lab.py > lab.log 2>&1 < /dev/null &
  sleep 4
}
echo "Runner: https://localhost:8902/runner"
echo
echo "The cert is self-signed. Open it in a Chrome started like this:"
echo "  google-chrome --user-data-dir=/tmp/cx-demo --ignore-certificate-errors \\"
echo "    https://localhost:8902/runner"
