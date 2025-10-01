# LiveKit Home-Agent Handoff

## Zielbild
Wir betreiben `home-agent` auf Fly.io als Voice-Agent-Cockpit mit Ready Player Me Avatar. Nutzer sollen das Web-UI unter `https://home-agent.fly.dev` öffnen, einen Avatar laden und sich mit einem LiveKit-Raum verbinden. Der Python-Agent (LiveKit Agents SDK) läuft im selben Container, nutzt OpenAI (STT/LLM/TTS) und bedient denselben Raum.

## Stack-Überblick
- **Frontend** (`index.html`, `server.js`): Express-Server liefert statische Assets und `/token`-Route, `model-viewer` rendert Ready Player Me GLB, LiveKit JS-Client verbindet den Browser.
- **Backend** (`main.py`, `startup.sh`): Python-Agent mit `livekit-agents`, Start via `startup.sh`, validiert Environment und startet Agent + Node-Frontend.
- **Deployment**: Fly.io Machine (`home-agent`). Dockerfile kombiniert Python + Node, Ports 80/443 proxen auf Express (`PORT=3000`). Secrets werden ausschließlich via `fly secrets set` konfiguriert.
- **LiveKit**: Externer Server/Cloud. Websocket-URL + API Keys kommen aus Env.

## Wichtige Dateien
- `server.js`: `/config.js` muss *vor* `express.static` registriert sein. Token-Route nutzt LiveKit `AccessToken`.
- `index.html`: `<model-viewer crossorigin="anonymous">`, keine `?pose=idle`-Parameter. Ready Player Me `postMessage`-Listener ignoriert Nicht-JSON.
- `startup.sh`: bricht ab, wenn `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, `OPENAI_API_KEY` fehlen; startet Python + Node.
- `fly.toml`: App-Name `home-agent`, legt nur Platzhalter-Env fest. Reale Werte via Secrets.
- `.gitignore`: `.env` und Logs ausgeschlossen.

## Environment / Secrets
Nicht im Repo einchecken! Auf Fly setzen:
```
fly secrets set \
  LIVEKIT_URL=wss://... \
  LIVEKIT_API_KEY=... \
  LIVEKIT_API_SECRET=... \
  OPENAI_API_KEY=sk-... \
  READY_PLAYER_ME_SUBDOMAIN=demo
```
Optional: weitere Provider (Deepgram etc.). Für lokale Tests: gleiche Variablen exportieren.

## LD3.5 / LangChain Kontext
Das Projekt war TLD für LD3.5 (interne Experimente). Der Voice-Agent nutzt LiveKit-Agents (Python) statt LangChain; LD3.5-Komponenten liegen außerhalb. Falls LD3.5 integriert wird, muss die Agent-Logik (z. B. `voice_ai_agent/`) an LiveKit angebunden und im Dockerfile berücksichtigt werden.

## Aktuelle Probleme & Fixes
- `/config.js` lieferte HTML → jetzt in `server.js` gefixt.
- Avatar-GLB 400-Fehler → `?pose=idle` entfernt, `crossorigin` gesetzt.
- Ready Player Me Messages → Robust parsing eingeführt.
- `.env` aus Repo entfernt.

## ToDo / Handover
1. Remotes setzen (`git remote add origin ...`), Commit `Fix cockpit config routing and avatar viewer` pushen.
2. Fly-Deployment ausführen (`fly deploy --app home-agent`).
3. Live-Test: Browser Cache löschen, `https://home-agent.fly.dev` öffnen, Avatar laden, Raum verbinden.
4. Agent Logs prüfen (`fly logs --app home-agent`) – bei Fehlern (Secrets/Audio) nachjustieren.

Bei Übergabe an einen nachfolgenden Agenten: dieses Dokument lesen, Repo clonen, Secrets setzen, Deploy anstoßen.
