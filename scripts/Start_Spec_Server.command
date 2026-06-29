#!/bin/bash
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/src/server"

python3 lenovo_spec_server.py &
PY_PID=$!

sleep 1.5

if [ -f "$ROOT/release/index.html" ]; then
  open "$ROOT/release/index.html"
else
  echo "release/index.html not found — run: npm run build"
  open "http://localhost:9527/"
fi

wait $PY_PID
