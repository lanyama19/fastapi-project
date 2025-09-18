#!/usr/bin/env bash
set -euo pipefail

LOCUST_FILE=${LOCUST_FILE:-/home/frank2025/app/src/loadtests/locust_v2.py}
HOST=${HOST:-http://127.0.0.1:8000}
USERS=${USERS:-200}
SPAWN_RATE=${SPAWN_RATE:-40}
RUN_TIME=${RUN_TIME:-10m}
LOG_DIR=${LOG_DIR:-$HOME/app/loadtest_logs}
DB_DSN=${DB_DSN:-}
SERVICE_NAME=${SERVICE_NAME:-fastapi}
SAMPLE_INTERVAL=${SAMPLE_INTERVAL:-2}

mkdir -p "$LOG_DIR"

run_id=$(date +%Y%m%d_%H%M%S)
locust_log="$LOG_DIR/locust_${run_id}.log"
csv_prefix="$LOG_DIR/locust_${run_id}"
system_log="$LOG_DIR/system_${run_id}.log"
db_log="$LOG_DIR/db_${run_id}.log"
svc_log="$LOG_DIR/${SERVICE_NAME}_journal_${run_id}.log"

pids=()
cleanup() {
  for pid in "${pids[@]:-}"; do
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
  done
}
trap cleanup EXIT INT TERM

if command -v pidstat >/dev/null 2>&1; then
  stdbuf -oL pidstat -rud -h "$SAMPLE_INTERVAL" >"$system_log" &
  pids+=($!)
else
  echo "pidstat not available; skipping detailed CPU metrics" >"$system_log"
fi

if command -v vmstat >/dev/null 2>&1; then
  stdbuf -oL vmstat "$SAMPLE_INTERVAL" >>"$system_log" &
  pids+=($!)
fi

if [[ -n "$DB_DSN" ]] && command -v psql >/dev/null 2>&1; then
  DB_DSN="$DB_DSN" DB_LOG="$db_log" SAMPLE_INTERVAL="$SAMPLE_INTERVAL" \
    stdbuf -oL bash -c 'while true; do
      psql "$DB_DSN" --csv -c "select now(), count(*) as active from pg_stat_activity;" >>"$DB_LOG"
      sleep "$SAMPLE_INTERVAL"
    done' &
  pids+=($!)
fi

if command -v journalctl >/dev/null 2>&1; then
  sudo journalctl -u "$SERVICE_NAME" -f --output cat >"$svc_log" &
  pids+=($!)
fi

locust -f "$LOCUST_FILE" \
  --host "$HOST" \
  --users "$USERS" \
  --spawn-rate "$SPAWN_RATE" \
  --run-time "$RUN_TIME" \
  --headless \
  --logfile "$locust_log" \
  --loglevel INFO \
  --csv "$csv_prefix" \
  --csv-full-history

echo "Locust log: $locust_log"
echo "Locust CSV prefix: ${csv_prefix}_*.csv"
echo "System metrics: $system_log"
if [[ -f "$db_log" ]]; then
  echo "DB metrics: $db_log"
fi
if [[ -f "$svc_log" ]]; then
  echo "Service log: $svc_log"
fi
