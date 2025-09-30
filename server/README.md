# Local LiveKit Server Setup

This directory contains a basic setup for running a local LiveKit server for development purposes.

## Prerequisites

- Docker
- Python with the LiveKit Agents package installed (already done in the parent directory)

## Starting the Server

1. Make sure Docker is running
2. Start the server (using Docker directly since Docker Compose may not be available):

```bash
./start_server.sh
```

3. The server will be available at:
   - WebSocket URL: `ws://localhost:7880`
   - HTTP endpoint: `http://localhost:7880` (for dashboard and REST API)

## Stopping the Server

```bash
./stop_server.sh
```

## Environment Variables

The server uses these credentials:
- API Key: `devkey`
- API Secret: `secret`
- URL: `ws://localhost:7880`

## Running Agents

To run the example agents:

1. Make sure the server is running
2. From the agents directory, run:

```bash
cd ../agents/
uv run python ../voice_ai_agent/main.py dev
```

For the voice agent, you'll also need to set the required API keys:

```bash
export OPENAI_API_KEY=your_openai_api_key_here
uv run python ../voice_ai_agent/main.py dev
```

## Testing Connection

You can test if the server is running correctly:

```bash
cd ../agents/
uv run python ../server/test_connection.py
```

## Configuration

The server configuration is in `config.yaml`. You can modify these settings:
- Port: 7880 (HTTP/WS)
- RTC TCP Port: 7881
- RTC UDP Port Range: 50000-60000
- Log Level: debug

## Troubleshooting

If the server doesn't start:
1. Check if ports 7880, 7881, and 50000-60000 are available
2. Check Docker logs: `docker logs -f livekit-server-dev`
3. Make sure Docker is running with sufficient permissions