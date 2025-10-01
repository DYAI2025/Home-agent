#!/bin/bash
set -euo pipefail

log() {
  echo "[startup] $1"
}

log "Starting Voice AI agent stack"

declare -a CHILD_PIDS=()

if [[ -n "${LIVEKIT_API_KEY:-}" && -n "${LIVEKIT_API_SECRET:-}" ]]; then
  python main.py &
  PYTHON_PID=$!
  CHILD_PIDS+=("${PYTHON_PID}")
  log "Python agent started with PID ${PYTHON_PID}"
else
  log "LIVEKIT credentials missing; skipping Python agent startup"
fi

npm start &
NODE_PID=$!
CHILD_PIDS+=("${NODE_PID}")
log "Frontend started with PID ${NODE_PID}"

cleanup() {
  log "Stopping services"
  for pid in "${CHILD_PIDS[@]}"; do
    kill "${pid}" 2>/dev/null || true
  done
  for pid in "${CHILD_PIDS[@]}"; do
    wait "${pid}" 2>/dev/null || true
  done
}

trap cleanup SIGINT SIGTERM

set +e
if ((${#CHILD_PIDS[@]} > 0)); then
  wait -n "${CHILD_PIDS[@]}"
  EXIT_CODE=$?
else
  EXIT_CODE=0
fi
set -e

cleanup

exit ${EXIT_CODE}
