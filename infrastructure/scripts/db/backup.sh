#!/usr/bin/env bash
# Local backup of the docker-compose PostgreSQL + Redis services.
#
# Scope: LOCAL / dev-like environments only — it talks to the `postgres` and `redis` services in
# docker-compose.yml. Production backup & DR cadence is an SRE responsibility (see the resilience
# plan; docs/data/migrations.md §6). Companion: restore.sh.
#
# IMPORTANT: audit_events / agent_memory_documents hold AES-256-GCM-encrypted L1/L2 fields
# (ADR-0018). This dump preserves the ciphertext; the DB_ENCRYPTION_KEY must be backed up SEPARATELY
# (Vault) or a restored dump is unreadable.
#
# Usage: infrastructure/scripts/db/backup.sh [OUTPUT_DIR]   (default ./backups)
set -euo pipefail

OUT_DIR="${1:-backups}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
PG_USER="${POSTGRES_USER:-appuser}"
PG_DB="${POSTGRES_DB:-appdb}"
REDIS_PW="${REDIS_PASSWORD:-devpassword}"

# Prefer `docker compose`; fall back to legacy `docker-compose`.
if docker compose version >/dev/null 2>&1; then DC="docker compose"; else DC="docker-compose"; fi

mkdir -p "$OUT_DIR"

echo "→ PostgreSQL dump (${PG_DB})…"
$DC exec -T postgres pg_dump -U "$PG_USER" "$PG_DB" | gzip > "${OUT_DIR}/postgres-${TS}.sql.gz"
echo "  wrote ${OUT_DIR}/postgres-${TS}.sql.gz"

echo "→ Redis snapshot…"
# SAVE forces a synchronous RDB write inside the container, then we copy it out.
$DC exec -T redis redis-cli -a "$REDIS_PW" --no-auth-warning SAVE >/dev/null
$DC cp redis:/data/dump.rdb "${OUT_DIR}/redis-${TS}.rdb"
echo "  wrote ${OUT_DIR}/redis-${TS}.rdb"

echo "✓ Backup complete (${TS}). Restore with: infrastructure/scripts/db/restore.sh ${OUT_DIR}/postgres-${TS}.sql.gz ${OUT_DIR}/redis-${TS}.rdb"
