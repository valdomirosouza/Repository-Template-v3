#!/usr/bin/env bash
# Restore the docker-compose PostgreSQL + Redis services from a backup.sh snapshot.
#
# Scope: LOCAL / dev-like environments only. DESTRUCTIVE — it overwrites the current data. Companion:
# backup.sh. Restored encrypted columns are only readable with the matching DB_ENCRYPTION_KEY.
#
# Usage: infrastructure/scripts/db/restore.sh <postgres-*.sql.gz> [redis-*.rdb]
set -euo pipefail

PG_DUMP="${1:?usage: restore.sh <postgres-*.sql.gz> [redis-*.rdb]}"
REDIS_RDB="${2:-}"
PG_USER="${POSTGRES_USER:-appuser}"
PG_DB="${POSTGRES_DB:-appdb}"

if docker compose version >/dev/null 2>&1; then DC="docker compose"; else DC="docker-compose"; fi

[ -f "$PG_DUMP" ] || { echo "ERROR: PostgreSQL dump not found: $PG_DUMP" >&2; exit 1; }

echo "⚠  This OVERWRITES the current ${PG_DB} database and Redis contents. Ctrl-C to abort."
read -r -p "   Type 'restore' to continue: " confirm
[ "$confirm" = "restore" ] || { echo "Aborted."; exit 1; }

echo "→ Restoring PostgreSQL (${PG_DB})…"
gunzip -c "$PG_DUMP" | $DC exec -T postgres psql -U "$PG_USER" -d "$PG_DB"
echo "  PostgreSQL restored."

if [ -n "$REDIS_RDB" ]; then
  [ -f "$REDIS_RDB" ] || { echo "ERROR: Redis RDB not found: $REDIS_RDB" >&2; exit 1; }
  echo "→ Restoring Redis (copy RDB + restart to load)…"
  $DC cp "$REDIS_RDB" redis:/data/dump.rdb
  $DC restart redis >/dev/null
  echo "  Redis restored."
else
  echo "→ Skipping Redis (no RDB argument given)."
fi

echo "✓ Restore complete. Verify with 'make smoke'."
