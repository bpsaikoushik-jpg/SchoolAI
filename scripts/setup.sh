#!/bin/bash
# SchoolAI local setup: prepares .env and builds/starts the full stack.
set -e

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo "No .env found — creating one from .env.example."
  cp .env.example .env
  echo "Edit .env now to set JWT_SECRET and at least one AI provider API key, then re-run this script."
  exit 0
fi

echo "Building images..."
docker compose build

echo "Starting stack (db -> backend -> frontend)..."
docker compose up -d

echo "Waiting for backend readiness..."
for i in $(seq 1 30); do
  if curl -sf http://localhost:8000/ready > /dev/null; then
    echo "Backend is ready."
    break
  fi
  sleep 2
done

echo "Done. Frontend: http://localhost:3000  Backend docs: http://localhost:8000/docs"
