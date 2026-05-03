#!/usr/bin/env bash
set -euo pipefail

# Load .env defaults
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Check if a port is available
is_port_free() {
    ! ss -tlnH "sport = :$1" 2>/dev/null | grep -q .
}

# Find first available port from a list, returns the chosen port
find_free_port() {
    local service_name="$1"
    shift
    for port in "$@"; do
        if is_port_free "$port"; then
            echo "$port"
            return 0
        fi
    done
    echo "ERROR: No free port found for $service_name (tried: $*)" >&2
    return 1
}

echo "=== SQL Playgrounds - Starting ==="
echo ""

# Resolve ports with fallbacks
POSTGRES_PORT=$(find_free_port "PostgreSQL" "${POSTGRES_PORT:-5432}" 5433 5434)
PGADMIN_PORT=$(find_free_port "PGAdmin" "${PGADMIN_PORT:-8080}" 8081 8082)
SUPERSET_PORT=$(find_free_port "Superset" "${SUPERSET_PORT:-8088}" 8089 8090)

export POSTGRES_PORT PGADMIN_PORT SUPERSET_PORT

echo "Ports:"
echo "  PostgreSQL : $POSTGRES_PORT"
echo "  PGAdmin    : $PGADMIN_PORT  -> http://localhost:$PGADMIN_PORT"
echo "  Superset   : $SUPERSET_PORT  -> http://localhost:$SUPERSET_PORT"
echo ""

# Pass through any extra args (e.g. --build, -d)
docker-compose up -d --build "$@"

echo ""
echo "=== All services started ==="
echo "  PGAdmin  : http://localhost:$PGADMIN_PORT"
echo "  Superset : http://localhost:$SUPERSET_PORT"
echo "  Postgres : localhost:$POSTGRES_PORT"
