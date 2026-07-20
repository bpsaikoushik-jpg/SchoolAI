#!/bin/bash
# SchoolAI deploy: pulls latest code, rebuilds images, applies migrations, restarts services.
# Run this ON YOUR SERVER — it assumes docker, docker compose, and a populated .env already exist there.
set -e

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo "ERROR: .env not found on this host. Copy .env.example to .env and fill in real production values first."
  exit 1
fi

echo "Pulling latest code..."
git pull

echo "Rebuilding images..."
docker compose build

echo "Recreating containers (migrations run automatically via backend entrypoint.sh)..."
docker compose up -d --force-recreate

echo "Waiting for backend readiness..."
for i in $(seq 1 30); do
  if curl -sf http://localhost:8000/ready > /dev/null; then
    echo "Backend is ready."
    docker compose ps
    exit 0
  fi
  sleep 2
done

echo "ERROR: backend did not become ready in time. Check logs with: docker compose logs backend"
exit 1
