#!/bin/bash
# Publish ARS Tool static UI to 1Panel website root.
set -euo pipefail

SRC="${XCLOUD_SRC:-/opt/ars-tool}"
DEST="${XCLOUD_WEB_ROOT:-/opt/1panel/www/sites/ars-tool/index}"
HTML_SRC="${SRC}/release/index.html"

sudo mkdir -p "$DEST"
sudo rsync -av "$HTML_SRC" "$DEST/index.html"
sudo chown -R 1000:1000 "$DEST"
sudo chmod 644 "$DEST/index.html"

echo "Published to $DEST/index.html"
echo ""
echo "Contents (requires sudo — AWP user may not read 1000:1000 dirs directly):"
sudo ls -la "$DEST"
