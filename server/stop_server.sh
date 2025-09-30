#!/bin/bash

# LiveKit Server Stop Script
# This script stops the LiveKit server

set -e

echo "Stopping LiveKit Server..."
docker stop livekit-server-dev > /dev/null 2>&1 || true
docker rm livekit-server-dev > /dev/null 2>&1 || true

echo "LiveKit Server stopped."