#!/bin/sh
set -e

echo "Waiting for database at ${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432}..."
python - <<'PYEOF'
import os
import socket
import time

host = os.getenv("POSTGRES_HOST", "db")
port = int(os.getenv("POSTGRES_PORT", "5432"))

for attempt in range(30):
    try:
        with socket.create_connection((host, port), timeout=2):
            print("Database is accepting connections.")
            break
    except OSError:
        print(f"DB not ready yet (attempt {attempt + 1}/30), retrying in 2s...")
        time.sleep(2)
else:
    raise SystemExit("Database never became reachable; aborting startup.")
PYEOF

echo "Running database migrations..."
alembic upgrade head

echo "Starting SchoolAI backend..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
