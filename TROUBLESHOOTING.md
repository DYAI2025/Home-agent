# Troubleshooting Notes

This document records the issues identified from the Fly.io logs and the corresponding fixes.

## 1. Python worker exited with usage message
- **Symptom:** The startup logs showed the Click usage screen (`Usage: main.py [OPTIONS] COMMAND [ARGS]...`) immediately after `Voice AI Agent is starting…`, followed by exit code `2`.
- **Root cause:** `main.py` invoked the LiveKit CLI without forwarding a command, which caused Click to exit before the worker bootstrapped.
- **Fix:** `main.py` now appends the default `start` command when no arguments are supplied and performs LiveKit credential checks before launching the worker.

## 2. LiveKit secrets misconfiguration
- **Symptom:** The worker exited with `api_key is required, or add LIVEKIT_API_KEY in your environment` when secrets were missing.
- **Fix:** Startup now verifies that `LIVEKIT_API_KEY` and `LIVEKIT_API_SECRET` are present. It logs a clear error and aborts gracefully if the secrets are absent, and performs a lightweight connectivity probe when they are available.

## 3. Token endpoint failed health checks
- **Symptom:** The Node.js `/token` route responded with a server error because `res.status(500).text(...)` is not a valid Express method.
- **Fix:** The handler now returns structured JSON errors and wraps token generation in a `try/catch` block for clearer diagnostics.

## 4. Corrupted cockpit UI
- **Symptom:** `index.html` contained two full HTML documents concatenated together, producing a broken front-end.
- **Fix:** The page was rewritten to a single cohesive cockpit that offers LiveKit controls, chat, and Ready Player Me integration. The UI now renders reliably and can be served directly by `server.js`.
