#!/bin/bash

# Complete Voice AI Agent Stop Script
# This script stops all components of the Voice AI Agent system

echo "================================="
echo "Voice AI Agent Stop Script"
echo "================================="

echo "Stopping Node.js frontend..."
pkill -f "node.*server.js" 2>/dev/null || true

echo "Stopping Python agent..."
pkill -f "python.*main.py" 2>/dev/null || true

echo "Stopping LiveKit server container..."
docker stop livekit-server-dev 2>/dev/null || true
docker rm livekit-server-dev 2>/dev/null || true

echo "Removing any background processes..."
pkill -f "start_all.sh" 2>/dev/null || true

echo
echo "================================="
echo "All components stopped!"
echo "================================="