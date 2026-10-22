#!/usr/bin/env bash
set -euo pipefail

BASE="${SD15_DAILY_GALLERY_DIR:-/home/darek123/python_projects/sd15-daily-gallery}"
mkdir -p "$BASE/logs"
exec >>"$BASE/logs/daily-$(date +%F).log" 2>&1

echo "[INFO] $(date --iso-8601=seconds) starting daily gallery generation"

set +e
/usr/bin/flock -n /tmp/sd15-daily-gallery.lock \
  /usr/bin/docker compose --project-directory "$BASE" run --rm generator
status=$?
set -e

if [ "$status" -eq 1 ]; then
  echo "[INFO] another generation is already running; skipped"
  exit 0
elif [ "$status" -ne 0 ]; then
  echo "[ERROR] generator exited with status $status"
  exit "$status"
fi

test -f "$BASE/output/latest.json"
test "$(find "$BASE/output" -maxdepth 1 -name 'image-*.webp' | wc -l)" -ge 5
echo "[INFO] generation completed"
