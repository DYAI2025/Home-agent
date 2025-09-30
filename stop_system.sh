#!/bin/bash

# Stop script for the Voice AI Agent system
# This script stops all components of the system

echo "Stopping Voice AI Agent system..."

# Kill the frontend and agent processes
pkill -f "node.*server.js" 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true

# Optionally stop the LiveKit Docker container
echo "Stopping LiveKit server container..."
docker stop livekit-server-dev 2>/dev/null || true

echo "All components stopped successfully!"