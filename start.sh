#!/usr/bin/env bash
set -Eeuo pipefail

echo "[start] applying Alembic migrations..."

# Retry alembic upgrade to tolerate DB cold starts on free instances
RETRIES=${ALEMBIC_RETRIES:-10}
DELAY=${ALEMBIC_RETRY_DELAY:-3}

attempt=1
until alembic upgrade head; do
  if [[ $attempt -ge $RETRIES ]]; then
    echo "[start] alembic upgrade failed after $RETRIES attempts. Exiting." >&2
    exit 1
  fi
  echo "[start] alembic upgrade failed (attempt $attempt/$RETRIES). Retrying in ${DELAY}s..."
  sleep "$DELAY"
  attempt=$((attempt + 1))
done

echo "[start] migrations applied. Launching app..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"

