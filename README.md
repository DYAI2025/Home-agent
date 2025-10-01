# Home Agent Fly.io Deployment

This branch packages the LiveKit voice agent, Ready Player Me cockpit, and supporting services so the full stack can be deployed on Fly.io.

## Components
- **Python agent (`main.py`)** - runs the LiveKit worker using `livekit-agents` with OpenAI STT/LLM/TTS.
- **Node/Express frontend (`server.js`, `index.html`)** - serves the cockpit UI and mints LiveKit access tokens.
- **Startup orchestration (`startup.sh`)** - launches the Python agent and frontend inside the Fly machine.
- **Dockerfile** - multi-runtime image (Python + Node) with audio dependencies (`ffmpeg`, `portaudio`).
- **fly.toml** - app configuration for Fly (`home-agent`).

## Prerequisites
1. Create a LiveKit project (self-hosted or Cloud) and note `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` (secret must be at least 32 characters).
2. Collect credentials required by the agent: at minimum `OPENAI_API_KEY`. Optional: `ANTHROPIC_API_KEY`, `MONGO_URI`, etc.
3. Install Fly CLI (`flyctl`) and log in: `fly auth login`.

## Local smoke test
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
npm install
export LIVEKIT_URL=wss://your-livekit-host
export LIVEKIT_API_KEY=devkey
export LIVEKIT_API_SECRET=lk_dev_secret_0123456789abcdef012345
export OPENAI_API_KEY=sk-...
./startup.sh
```
Open http://localhost:3000, load an avatar, and connect to a room that your LiveKit server hosts.

## Deploy to Fly.io
```bash
fly launch --name home-agent --no-deploy
fly ips allocate-v4             # optional dedicated IPv4
fly secrets set \
  LIVEKIT_URL=wss://... \
  LIVEKIT_API_KEY=... \
  LIVEKIT_API_SECRET=... \
  OPENAI_API_KEY=... \
  READY_PLAYER_ME_SUBDOMAIN=demo
fly deploy
```

### Troubleshooting
- `missing required environment variable` during boot: set secrets with `fly secrets set ...`.
- `failed to wait for VM ... not found`: rerun `fly deploy`; ensure app name matches `fly.toml` (`home-agent`).
- No audio or LLM response: confirm LiveKit credentials, the OpenAI key, and that the agent process is healthy (`fly logs`).

## Branch structure
This branch (`fly-branch`) tracks Fly-specific configuration. Merge back to `main` once validated or keep it as a deployment branch.
