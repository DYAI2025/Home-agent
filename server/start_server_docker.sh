#!/bin/bash

# LiveKit Server Startup Script (Docker direct)
# This script starts the LiveKit server for local development using Docker directly

set -e

echo "Starting LiveKit Server for local development..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running or accessible"
    exit 1
fi

# Stop any existing container with the same name
if docker ps -a --format "table {{.Names}}" | grep -q "^livekit-server-dev$"; then
    echo "Stopping existing LiveKit server container..."
    docker stop livekit-server-dev > /dev/null 2>&1 || true
    docker rm livekit-server-dev > /dev/null 2>&1 || true
fi

# Run the LiveKit server container directly
echo "Starting LiveKit server container..."
docker run -d \\
  --name livekit-server-dev \\
  --restart unless-stopped \\
  -p 7880:7880 \\
  -p 7881:7881 \\
  -p 50000-60000:50000-60000/udp \\
  -e LIVEKIT_PORT=7880 \\
  -e LIVEKIT_RTC_UDPPORT=50000-60000 \\
  -e LIVEKIT_RTC_TCPPORT=7881 \\
  -e LIVEKIT_KEYS={"devkey": "secret"} \\
  -e LIVEKIT_LOG_LEVEL=debug \\
  -e LIVEKIT_ENABLE_TURN=true \\
  -e LIVEKIT_TURN_PORT_RANGE_START=30000 \\
  -e LIVEKIT_TURN_PORT_RANGE_END=40000 \\
  -e LIVEKIT_TURN_LISTEN_ADDRESSES=0.0.0.0 \\
  -v "$(pwd)/config.yaml:/config.yaml" \\
  livekit/livekit-server:latest \\
  --config /config.yaml

echo "LiveKit Server is starting..."
echo "URL: ws://localhost:7880"
echo "Dashboard: http://localhost:7880"
echo ""
echo "To view server logs:"
echo "  docker logs -f livekit-server-dev"
echo ""
echo "Server should be ready in about 10 seconds."

# Wait a bit for the server to start
sleep 10

# Test the connection
if curl -f http://localhost:7880/ > /dev/null 2>&1; then
    echo "✓ LiveKit Server is running and accessible!"
    echo "Environment variables for your agent:"
    echo "  LIVEKIT_URL=ws://localhost:7880"
    echo "  LIVEKIT_API_KEY=devkey"
    echo "  LIVEKIT_API_SECRET=secret"
else
    echo "! Warning: Could not reach the server at http://localhost:7880"
    echo "Check server logs with: docker logs -f livekit-server-dev"
fi

