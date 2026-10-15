#!/usr/bin/env bash
#
# Builds the stack, runs the integration tests, and always tears down.
# Exits with the test-runner's exit code.

set -euo pipefail

cleanup() {
  local rc=$?
  set +e
  echo "=== Tearing down test environment ==="
  docker compose down --volumes --remove-orphans
  exit "$rc"
}
trap cleanup EXIT

echo "=== [1/2] Building images ==="
docker compose build

echo "=== [2/2] Running integration tests ==="
docker compose up --abort-on-container-exit --exit-code-from test-runner
