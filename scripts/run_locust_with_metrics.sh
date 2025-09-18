#!/usr/bin/env bash
set -euo pipefail

LOCUST_FILE=${LOCUST_FILE:-/home/frank2025/app/src/loadtests/locust_v2.py}
HOST=${HOST:-http://127.0.0.1:8000}
USERS=${USERS:-200}
SPAWN_RATE=${SPAWN_RATE:-40}
RUN_TIME=${RUN_TIME:-10m}
DB_DSN=${DB_DSN:-}
SERVICE_NAME=${SERVICE_NAME:-fastapi}
SAMPLE_INTERVAL=${SAMPLE_INTERVAL:-2}
PYTHON_BIN=${PYTHON_BIN:-python}
SEED_COUNT=${SEED_COUNT:-$USERS}
SEED_PASSWORD=${SEED_PASSWORD:-LoadTest!234}

if ! LOCUST_DIR=$(cd "$(dirname "${LOCUST_FILE}")" 2>/dev/null && pwd); then
  echo "Unable to resolve directory for LOCUST_FILE=${LOCUST_FILE}" >&2
  exit 1
fi

SIM_OUTPUT_DIR=${SIM_OUTPUT_DIR:-${LOCUST_DIR}/sim_res}
SEED_SCRIPT=${SEED_SCRIPT:-${LOCUST_DIR}/seed_test_users.py}
USERS_FILE=${USERS_FILE:-${SIM_OUTPUT_DIR}/test_users.json}
LOG_DIR=${LOG_DIR:-${SIM_OUTPUT_DIR}}

mkdir -p "$LOG_DIR"
mkdir -p "$(dirname "$USERS_FILE")"

if [[ -f "$SEED_SCRIPT" ]]; then
  echo "Seeding $SEED_COUNT users via $SEED_SCRIPT"
  "$PYTHON_BIN" "$SEED_SCRIPT" \
    --count "$SEED_COUNT" \
    --password "$SEED_PASSWORD" \
    --output "$USERS_FILE"
else
  echo "Warning: seed script $SEED_SCRIPT not found; skipping user creation" >&2
fi

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
      sleep '$SAMPLE_INTERVAL'
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
  --csv-full-history \
  --users-file "$USERS_FILE"

echo "Locust log: $locust_log"
echo "Locust CSV prefix: ${csv_prefix}_*.csv"
echo "System metrics: $system_log"
if [[ -f "$db_log" ]]; then
  echo "DB metrics: $db_log"
fi
if [[ -f "$svc_log" ]]; then
  echo "Service log: $svc_log"
fi
