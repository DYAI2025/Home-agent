#!/bin/bash
set -euo pipefail

log() {
  echo "[startup] $1"
}

log "Starting Voice AI agent stack"

missing_var=false
for required in LIVEKIT_URL LIVEKIT_API_KEY LIVEKIT_API_SECRET OPENAI_API_KEY; do
  if [ -z "${!required:-}" ]; then
    log "Missing required environment variable: $required"
    missing_var=true
  fi
done

if [ "$missing_var" = true ]; then
  log "Set the variables above (use 'fly secrets set' in production)."
  exit 1
fi

python main.py &
PYTHON_PID=$!
log "Python agent started with PID ${PYTHON_PID}"

npm start &
NODE_PID=$!
log "Frontend started with PID ${NODE_PID}"

cleanup() {
  log "Stopping services"
  kill ${PYTHON_PID} ${NODE_PID} 2>/dev/null || true
  wait ${PYTHON_PID} ${NODE_PID} 2>/dev/null || true
}

trap cleanup SIGINT SIGTERM

set +e
wait -n ${PYTHON_PID} ${NODE_PID}
EXIT_CODE=$?
set -e

cleanup

exit ${EXIT_CODE}
